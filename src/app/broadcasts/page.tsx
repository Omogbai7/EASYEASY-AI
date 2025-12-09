"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface Broadcast {
  id: number;
  promo_id: number;
  total_recipients: number;
  sent_count: number;
  failed_count: number;
  status: string;
  created_at: string;
  completed_at: string | null;
}

export default function BroadcastsPage() {
  const [broadcasts, setBroadcasts] = useState<Broadcast[]>([]);
  const [loading, setLoading] = useState(true);

  // 1. Get the real API link from Railway
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchBroadcasts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchBroadcasts = async () => {
    try {
      // 2. FIX: Use the variable, NOT localhost
      const response = await fetch(`${apiUrl}/api/broadcasts`);
      
      // 3. Safety Check: If the URL is wrong, don't crash
      if (!response.ok) throw new Error("Failed to fetch data");

      const data = await response.json();
      setBroadcasts(data.broadcasts || []);
    } catch (error) {
      console.error('Error fetching broadcasts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      in_progress: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800"
    };
    return <Badge className={variants[status] || ""}>{status.toUpperCase()}</Badge>;
  };

  const totalSent = broadcasts.reduce((sum, b) => sum + b.sent_count, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="border-b bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Broadcasts</h1>
              <p className="text-sm text-slate-600 mt-1">Promotion broadcast history</p>
            </div>
            <Link href="/">
              <Button variant="outline">← Back to Dashboard</Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        {/* ... (Rest of your UI code remains exactly the same) ... */}
        
        {/* Just paste the rest of your JSX here (Cards, Tables, etc.) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-600">Total Broadcasts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                {broadcasts.length}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-600">Messages Sent</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {totalSent.toLocaleString()}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-600">Success Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {broadcasts.length > 0
                  ? Math.round((totalSent / broadcasts.reduce((sum, b) => sum + b.total_recipients, 0)) * 100)
                  : 0
                }%
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white shadow-md">
          <CardHeader>
            <CardTitle>Broadcast History</CardTitle>
            <CardDescription>
              All broadcast campaigns
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading broadcasts...</div>
            ) : broadcasts.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No broadcasts found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Promo ID</TableHead>
                    <TableHead>Recipients</TableHead>
                    <TableHead>Sent</TableHead>
                    <TableHead>Failed</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {broadcasts.map((broadcast) => (
                    <TableRow key={broadcast.id}>
                      <TableCell className="font-medium">#{broadcast.id}</TableCell>
                      <TableCell>#{broadcast.promo_id}</TableCell>
                      <TableCell>{broadcast.total_recipients}</TableCell>
                      <TableCell className="text-green-600 font-semibold">
                        {broadcast.sent_count}
                      </TableCell>
                      <TableCell className="text-red-600 font-semibold">
                        {broadcast.failed_count}
                      </TableCell>
                      <TableCell>{getStatusBadge(broadcast.status)}</TableCell>
                      <TableCell>
                        {new Date(broadcast.created_at).toLocaleDateString()}
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