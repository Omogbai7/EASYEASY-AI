"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ShieldCheck, Eye, CheckCircle } from "lucide-react";

interface Vendor {
  id: number;
  name: string;
  business_name: string;
  phone_number: string;
  verification_status: string;
  created_at: string;
  verification_doc?: string;
}

export default function VerificationsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);

  // 1. Use the environment variable
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchVendors();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchVendors = async () => {
    try {
      // 2. FIX: Fetch from '/api/users' (not stats)
      const response = await fetch(`${apiUrl}/api/users?role=vendor`);
      const data = await response.json();
      
      // Filter for pending or verified
      const relevantVendors = (data.users || []).filter((u: Vendor) => 
        u.verification_status === 'pending' || u.verification_status === 'verified'
      );
      
      setVendors(relevantVendors);
    } catch (error) {
      console.error('Error fetching vendors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (id: number) => {
    if (!confirm("Approve this vendor?")) return;
    
    try {
      const res = await fetch(`${apiUrl}/api/users/${id}/verify`, { method: 'POST' });
      if (res.ok) {
        alert("Vendor Verified!");
        setVendors(vendors.map(v => v.id === id ? { ...v, verification_status: 'verified' } : v));
      }
    } catch (error) {
      alert("Error verifying vendor");
    }
  };

  const handleReject = async (id: number) => {
    if (!confirm("Reject this document?")) return;
    
    try {
      const res = await fetch(`${apiUrl}/api/users/${id}/reject_verification`, { method: 'POST' });
      if (res.ok) {
        alert("Vendor Rejected.");
        // Remove from list
        setVendors(vendors.filter(v => v.id !== id));
      }
    } catch (error) {
      alert("Error rejecting vendor");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Vendor Documents</h1>
            <p className="text-sm text-slate-600">Review uploaded IDs and Bills</p>
          </div>
          <Link href="/">
            <Button variant="outline">← Back to Dashboard</Button>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <Card className="bg-white shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-blue-600" />
              Submissions ({vendors.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="py-8 text-center text-slate-500">Loading...</div>
            ) : vendors.length === 0 ? (
              <div className="py-12 text-center text-slate-500">No documents found.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Vendor</TableHead>
                    <TableHead>Business</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Document</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {vendors.map((vendor) => (
                    <TableRow key={vendor.id}>
                      <TableCell>
                        <div className="font-medium">{vendor.name}</div>
                        <div className="text-xs text-slate-500">{vendor.phone_number}</div>
                      </TableCell>
                      <TableCell>{vendor.business_name}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={vendor.verification_status === 'verified' ? 'default' : 'destructive'}
                          className={vendor.verification_status === 'verified' ? 'bg-green-600' : 'bg-orange-500'}
                        >
                          {vendor.verification_status.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {vendor.verification_doc ? (
                          // 3. FIX: Use dynamic apiUrl link
                          <a 
                            href={`${apiUrl}/api/media/${vendor.verification_doc}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                          >
                            <Button size="sm" variant="secondary" className="gap-2">
                              <Eye className="w-4 h-4" /> View Doc
                            </Button>
                          </a>
                        ) : (
                          <span className="text-slate-400 text-sm italic">No doc</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        {vendor.verification_status === 'pending' && (
                          <div className="flex justify-end gap-2">
                            <Button 
                              size="sm" 
                              className="bg-green-600 hover:bg-green-700"
                              onClick={() => handleVerify(vendor.id)}
                            >
                              Approve
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleReject(vendor.id)}
                            >
                              Decline
                            </Button>
                          </div>
                        )}
                        {vendor.verification_status === 'verified' && (
                          <div className="flex items-center justify-end gap-1 text-green-600 text-sm font-medium">
                            <CheckCircle className="w-4 h-4" /> Verified
                          </div>
                        )}
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