"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface User {
  id: number;
  phone_number: string;
  name: string;
  role: string;
  interests: string; 
  created_at: string;
  is_active: boolean;
}

export default function SubscribersPage() {
  const [subscribers, setSubscribers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  // 1. Get API URL from Environment Variable
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchSubscribers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchSubscribers = async () => {
    try {  
      // 2. FIX: Fetch from '/api/users' with role filter, NOT '/api/stats'
      const response = await fetch(`${apiUrl}/api/users?role=subscriber`);
      
      if (!response.ok) throw new Error("Failed to fetch data");

      const data = await response.json();
      
      // 3. Safety: Ensure we set an array, even if empty
      setSubscribers(data.users || []);
    } catch (error) {
      console.error('Error fetching subscribers:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="border-b bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Subscribers</h1>
              <p className="text-sm text-slate-600 mt-1">Manage subscribers and users</p>
            </div>
            <Link href="/">
              <Button variant="outline">← Back to Dashboard</Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <Card className="bg-white shadow-md">
          <CardHeader>
            <CardTitle>Subscribers List</CardTitle>
            <CardDescription>
              {subscribers.length} subscriber{subscribers.length !== 1 ? 's' : ''} registered
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading subscribers...</div>
            ) : subscribers.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No subscribers found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Phone</TableHead>
                    <TableHead>Interests</TableHead>
                    <TableHead>Joined</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {subscribers.map((subscriber) => (
                    <TableRow key={subscriber.id}>
                      <TableCell className="font-medium">#{subscriber.id}</TableCell>
                      <TableCell>{subscriber.phone_number}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {/* Handle comma-separated interests string safely */}
                          {subscriber.interests && subscriber.interests !== "No interests set" ? (
                            subscriber.interests.split(',').map((interest, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {interest.trim()}
                              </Badge>
                            ))
                          ) : (
                            <span className="text-slate-500 text-sm">No interests set</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(subscriber.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant={subscriber.is_active ? 'default' : 'secondary'}>
                          {subscriber.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}