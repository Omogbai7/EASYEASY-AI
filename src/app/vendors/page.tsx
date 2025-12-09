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
  business_name: string;
  business_description: string;
  created_at: string;
  is_active: boolean;
}

export default function VendorsPage() {
  const [vendors, setVendors] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  // 1. Get API URL from Environment Variable
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchVendors();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchVendors = async () => {
    try {
      // 2. FIX: Fetch from '/api/users?role=vendor', NOT '/api/stats'
      const response = await fetch(`${apiUrl}/api/users?role=vendor`);
      
      if (!response.ok) throw new Error("Failed to fetch vendors");

      const data = await response.json();
      
      // 3. Safety: Ensure we set an array
      setVendors(data.users || []);
    } catch (error) {
      console.error('Error fetching vendors:', error);
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
              <h1 className="text-3xl font-bold text-slate-900">Vendors</h1>
              <p className="text-sm text-slate-600 mt-1">Manage business vendors</p>
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
            <CardTitle>Vendors List</CardTitle>
            <CardDescription>
              {vendors.length} vendor{vendors.length !== 1 ? 's' : ''} registered
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading vendors...</div>
            ) : vendors.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No vendors found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Business</TableHead>
                    <TableHead>Phone</TableHead>
                    <TableHead>Joined</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {vendors.map((vendor) => (
                    <TableRow key={vendor.id}>
                      <TableCell className="font-medium">#{vendor.id}</TableCell>
                      <TableCell>{vendor.name || 'N/A'}</TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{vendor.business_name || 'N/A'}</div>
                          <div className="text-sm text-slate-500 max-w-xs truncate">
                            {vendor.business_description || 'No description'}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{vendor.phone_number}</TableCell>
                      <TableCell>
                        {new Date(vendor.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant={vendor.is_active ? 'default' : 'secondary'}>
                          {vendor.is_active ? 'Active' : 'Inactive'}
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