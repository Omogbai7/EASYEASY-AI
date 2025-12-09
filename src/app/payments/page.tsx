"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface Payment {
  id: number;
  user_id: number;
  promo_id: number;
  amount: number;
  reference: string;
  status: string;
  payment_method: string;
  paystack_reference: string;
  created_at: string;
  completed_at: string | null;
}

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<number | null>(null);

  // 1. Define the API URL once using the environment variable
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchPayments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchPayments = async () => {
    try {
      // 2. FIX: Fetch from '/api/payments', NOT '/api/stats'
      const response = await fetch(`${apiUrl}/api/payments`);
      
      if (!response.ok) throw new Error("Failed to fetch payments");
      
      const data = await response.json();
      // Ensure we always have an array to prevent crashes
      setPayments(data.payments || []); 
    } catch (error) {
      console.error('Error fetching payments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmPayment = async (paymentId: number) => {
    const isConfirmed = window.confirm("Have you verified this payment on Flutterwave?");
    if (!isConfirmed) return;

    setProcessingId(paymentId);

    try {
      // 3. FIX: Use the variable 'apiUrl', do not use hardcoded localhost
      const response = await fetch(`${apiUrl}/api/payments/${paymentId}/confirm`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        setPayments(payments.map(p => 
          p.id === paymentId ? { ...p, status: 'completed', completed_at: new Date().toISOString() } : p
        ));
        alert("Payment marked as completed!");
      } else {
        alert("Failed to update payment: " + data.message);
      }
    } catch (error) {
      console.error('Error confirming payment:', error);
      alert("Error connecting to server");
    } finally {
      setProcessingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
      completed: "bg-green-100 text-green-800 hover:bg-green-100",
      failed: "bg-red-100 text-red-800 hover:bg-red-100"
    };
    return <Badge className={variants[status] || ""}>{status.toUpperCase()}</Badge>;
  };

  const totalRevenue = payments
    .filter(p => p.status === 'completed')
    .reduce((sum, p) => sum + p.amount, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="border-b bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Payments</h1>
              <p className="text-sm text-slate-600 mt-1">Transaction history and revenue</p>
            </div>
            <Link href="/">
              <Button variant="outline">← Back to Dashboard</Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-600">Total Revenue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                ₦{totalRevenue.toLocaleString()}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-600">Total Transactions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                {payments.length}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-600">Completed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {payments.filter(p => p.status === 'completed').length}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white shadow-md">
          <CardHeader>
            <CardTitle>Payments List</CardTitle>
            <CardDescription>
              All payment transactions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading payments...</div>
            ) : payments.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No payments found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Reference</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Completed</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payments.map((payment) => (
                    <TableRow key={payment.id}>
                      <TableCell className="font-medium">#{payment.id}</TableCell>
                      <TableCell className="font-mono text-sm">{payment.reference}</TableCell>
                      <TableCell className="font-semibold">
                        ₦{payment.amount.toLocaleString()}
                      </TableCell>
                      <TableCell>{getStatusBadge(payment.status)}</TableCell>
                      <TableCell>
                        {new Date(payment.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {payment.completed_at
                          ? new Date(payment.completed_at).toLocaleDateString()
                          : '-'
                        }
                      </TableCell>
                      <TableCell className="text-right">
                        {payment.status === 'pending' && (
                          <Button 
                            size="sm" 
                            className="bg-green-600 hover:bg-green-700 text-white"
                            onClick={() => handleConfirmPayment(payment.id)}
                            disabled={processingId === payment.id}
                          >
                            {processingId === payment.id ? "..." : "Mark Paid"}
                          </Button>
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