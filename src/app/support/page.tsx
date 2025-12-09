"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface Ticket {
  id: number;
  user_name: string;
  user_phone: string;
  message: string;
  status: string;
  created_at: string;
}

export default function SupportPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/stats`);
      const data = await response.json();
      setTickets(data.tickets);
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (id: number) => {
    if (!confirm("Mark this ticket as resolved?")) return;
    
    try {
      await fetch(`http://localhost:5000/api/support/${id}/resolve`, { method: 'POST' });
      // Update UI locally
      setTickets(tickets.map(t => t.id === id ? { ...t, status: 'resolved' } : t));
    } catch (error) {
      alert("Error updating ticket");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Support Tickets</h1>
            <p className="text-sm text-slate-600">User complaints and messages</p>
          </div>
          <Link href="/">
            <Button variant="outline">← Back to Dashboard</Button>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Complaints</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="py-8 text-center">Loading tickets...</div>
            ) : tickets.length === 0 ? (
              <div className="py-8 text-center text-slate-500">No active tickets found.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Message</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tickets.map((ticket) => (
                    <TableRow key={ticket.id}>
                      <TableCell className="whitespace-nowrap text-sm text-slate-500">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="font-medium">{ticket.user_name}</div>
                        <div className="text-xs text-slate-500">{ticket.user_phone}</div>
                      </TableCell>
                      <TableCell className="max-w-md truncate" title={ticket.message}>
                        {ticket.message}
                      </TableCell>
                      <TableCell>
                        <Badge variant={ticket.status === 'open' ? 'destructive' : 'default'}>
                          {ticket.status.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        {ticket.status === 'open' && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleResolve(ticket.id)}
                          >
                            Mark Resolved
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