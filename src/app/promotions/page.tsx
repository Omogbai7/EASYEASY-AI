"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MessageSquare, Check, X, Send, Eye } from "lucide-react";

interface Promo {
  id: number;
  vendor_name: string;
  vendor_business: string;
  title: string;
  description: string;
  price: number;
  contact_info: string;
  media_url: string;
  media_type: string;
  promo_type: string;
  ai_generated_caption: string;
  status: string;
  category: string;
  created_at: string;
  approved_at: string | null;
  broadcasted_at: string | null;
  views: number;
  clicks: number;
}

export default function PromotionsPage() {
  const [promos, setPromos] = useState<Promo[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [selectedPromo, setSelectedPromo] = useState<Promo | null>(null);

  useEffect(() => {
    fetchPromos();
  }, [filter]);

  const fetchPromos = async () => {
    try {
      const url = filter === "all"
        ? 'http://localhost:5000/api/promos'
        : `http://localhost:5000/api/promos?status=${filter}`;
      const response = await fetch(url);
      const data = await response.json();
      setPromos(data.promos);
    } catch (error) {
      console.error('Error fetching promos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (promoId: number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/promos/${promoId}/approve`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchPromos();
      }
    } catch (error) {
      console.error('Error approving promo:', error);
    }
  };

  const handleReject = async (promoId: number) => {
    const reason = prompt("Reason for rejection:");
    if (!reason) return;

    try {
      const response = await fetch(`http://localhost:5000/api/promos/${promoId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      if (response.ok) {
        fetchPromos();
      }
    } catch (error) {
      console.error('Error rejecting promo:', error);
    }
  };

  const handleBroadcast = async (promoId: number) => {
    if (!confirm("Are you sure you want to broadcast this promotion to all relevant subscribers?")) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/promos/${promoId}/broadcast`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        alert(`Successfully broadcasted to ${data.sent_count} users!`);
        fetchPromos();
      }
    } catch (error) {
      console.error('Error broadcasting promo:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      approved: "bg-green-100 text-green-800",
      rejected: "bg-red-100 text-red-800",
      broadcasted: "bg-blue-100 text-blue-800"
    };
    return <Badge className={variants[status] || ""}>{status.toUpperCase()}</Badge>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Promotions</h1>
              <p className="text-sm text-slate-600 mt-1">Manage and broadcast promotions</p>
            </div>
            <Link href="/">
              <Button variant="outline">← Back to Dashboard</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Filters */}
      <div className="container mx-auto px-6 py-6">
        <Card className="bg-white shadow-md mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Filter Promotions</CardTitle>
              <Select value={filter} onValueChange={setFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Promotions</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="broadcasted">Broadcasted</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
        </Card>

        {/* Promotions Table */}
        <Card className="bg-white shadow-md">
          <CardHeader>
            <CardTitle>Promotions List</CardTitle>
            <CardDescription>
              {promos.length} promotion{promos.length !== 1 ? 's' : ''} found
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading promotions...</div>
            ) : promos.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No promotions found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Vendor</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Analytics</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {promos.map((promo) => (
                    <TableRow key={promo.id}>
                      <TableCell className="font-medium">#{promo.id}</TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{promo.vendor_name}</div>
                          <div className="text-sm text-slate-500">{promo.vendor_business}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <div className="font-medium truncate">{promo.title}</div>
                          <div className="text-sm text-slate-500 truncate">{promo.description}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {promo.price > 0 ? `₦${promo.price.toLocaleString()}` : "Free"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={promo.promo_type === 'paid' ? 'default' : 'secondary'}>
                          {promo.promo_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{getStatusBadge(promo.status)}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>👁 {promo.views} views</div>
                          <div>🖱 {promo.clicks} clicks</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedPromo(promo)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          {promo.status === 'pending' && (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-green-600 hover:text-green-700"
                                onClick={() => handleApprove(promo.id)}
                              >
                                <Check className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-red-600 hover:text-red-700"
                                onClick={() => handleReject(promo.id)}
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </>
                          )}
                          {promo.status === 'approved' && (
                            <Button
                              size="sm"
                              className="bg-blue-600 hover:bg-blue-700"
                              onClick={() => handleBroadcast(promo.id)}
                            >
                              <Send className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Promo Details Modal */}
        {selectedPromo && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Promotion Details</CardTitle>
                  <Button variant="outline" onClick={() => setSelectedPromo(null)}>Close</Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Title</h3>
                  <p>{selectedPromo.title}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Description</h3>
                  <p>{selectedPromo.description}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">AI Generated Caption</h3>
                  <p className="bg-slate-50 p-3 rounded">{selectedPromo.ai_generated_caption}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-semibold mb-2">Price</h3>
                    <p>{selectedPromo.price > 0 ? `₦${selectedPromo.price.toLocaleString()}` : "Free"}</p>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">Contact Info</h3>
                    <p>{selectedPromo.contact_info}</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Vendor</h3>
                  <p>{selectedPromo.vendor_name} - {selectedPromo.vendor_business}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Status</h3>
                  {getStatusBadge(selectedPromo.status)}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
