"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Users,
  ShoppingBag,
  DollarSign,
  MessageSquare,
  CheckCircle,
  Clock,
  Send,
  LifeBuoy, // New Icon for Support
  ShieldCheck
} from "lucide-react";

interface Stats {
  total_users: number;
  total_vendors: number;
  total_subscribers: number;
  total_promos: number;
  pending_promos: number;
  approved_promos: number;
  broadcasted_promos: number;
  total_revenue: number;
}

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">EasyEasy Admin</h1>
              <p className="text-sm text-slate-600 mt-1">WhatsApp Bot Management Dashboard</p>
            </div>
            <MessageSquare className="w-10 h-10 text-green-600" />
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="container mx-auto px-6">
          <div className="flex space-x-8 py-4 overflow-x-auto">
            <Link href="/" className="text-slate-900 font-semibold border-b-2 border-green-600 pb-1 whitespace-nowrap">
              Dashboard
            </Link>
            <Link href="/vendors" className="text-slate-600 hover:text-slate-900 transition whitespace-nowrap">
              Vendors
            </Link>
            <Link href="/subscribers" className="text-slate-600 hover:text-slate-900 transition whitespace-nowrap">
              Subscribers
            </Link>
            <Link href="/promotions" className="text-slate-600 hover:text-slate-900 transition whitespace-nowrap">
              Promotions
            </Link>
            <Link href="/payments" className="text-slate-600 hover:text-slate-900 transition whitespace-nowrap">
              Payments
            </Link>
            <Link href="/broadcasts" className="text-slate-600 hover:text-slate-900 transition whitespace-nowrap">
              Broadcasts
            </Link>
            <Link href="/support" className="text-slate-600 hover:text-slate-900 transition whitespace-nowrap">
              Support
            </Link>
            <Link href="/verifications" className="text-slate-600 hover:text-slate-900 transition whitespace-nowrap">
              Verifications
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white shadow-md hover:shadow-lg transition">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Total Users
              </CardTitle>
              <Users className="w-5 h-5 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                {stats?.total_users || 0}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {stats?.total_vendors || 0} vendors • {stats?.total_subscribers || 0} subscribers
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md hover:shadow-lg transition">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Total Promotions
              </CardTitle>
              <ShoppingBag className="w-5 h-5 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                {stats?.total_promos || 0}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {stats?.pending_promos || 0} pending approval
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md hover:shadow-lg transition">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Broadcasted
              </CardTitle>
              <Send className="w-5 h-5 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                {stats?.broadcasted_promos || 0}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {stats?.approved_promos || 0} approved, ready to send
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md hover:shadow-lg transition">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Total Revenue
              </CardTitle>
              <DollarSign className="w-5 h-5 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                ₦{stats?.total_revenue?.toLocaleString() || 0}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                From paid promotions
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <h2 className="text-xl font-bold text-slate-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-orange-600" />
                Pending Approvals
              </CardTitle>
              <CardDescription>
                {stats?.pending_promos || 0} promotions waiting for review
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/promotions?status=pending">
                <Button className="w-full bg-orange-600 hover:bg-orange-700">
                  Review Pending Promos
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Ready to Broadcast
              </CardTitle>
              <CardDescription>
                {stats?.approved_promos || 0} approved promotions ready to send
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/promotions?status=approved">
                <Button className="w-full bg-green-600 hover:bg-green-700">
                  View Approved Promos
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* ADDED: Support Ticket Action */}
          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LifeBuoy className="w-5 h-5 text-blue-600" />
                Support Tickets
              </CardTitle>
              <CardDescription>
                View and resolve user complaints
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/support">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  View Support Inbox
                </Button>
              </Link>
            </CardContent>
          </Card>
      
        {/* ADD THIS TO QUICK ACTIONS GRID */}
          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-600" />
                Verifications
              </CardTitle>
              <CardDescription>
                Approve new vendor documents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/verifications">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  Review Docs
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>  
        {/* System Info */}
        <Card className="bg-white shadow-md">
          <CardHeader>
            <CardTitle>System Information</CardTitle>
            <CardDescription>EasyEasy WhatsApp Bot Configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-slate-700 mb-2">Backend Status</h3>
                <p className="text-sm text-slate-600">Python Flask API running on port 5000</p>
                <p className="text-sm text-green-600 font-medium mt-1">✓ Connected</p>
              </div>
              <div>
                <h3 className="font-semibold text-slate-700 mb-2">Features Active</h3>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li>✓ WhatsApp Business API</li>
                  <li>✓ Flutterwave Manual Verify</li>
                  <li>✓ OpenAI Ad Generation</li>
                  <li>✓ Gender & Interest Targeting</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}