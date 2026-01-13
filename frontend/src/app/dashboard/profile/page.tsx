'use client';

import { useState, useEffect } from 'react';
import { userApi, subscriptionApi, imageApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, Plan, Subscription, ImageRecord } from '@/types';

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [history, setHistory] = useState<ImageRecord[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const [userData, subData, plansData, historyData] = await Promise.all([
        userApi.getMe(),
        subscriptionApi.getMy(),
        subscriptionApi.getPlans(),
        imageApi.getHistory(),
      ]);
      setUser(userData);
      setEmail(userData.email);
      setUsername(userData.username);
      setSubscription(subData);
      setPlans(plansData);
      setHistory(historyData);
    } catch (err) {
      setError('Failed to load user data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const updates: any = {};
      if (email !== user?.email) updates.email = email;
      if (username !== user?.username) updates.username = username;
      if (password) updates.password = password;

      await userApi.updateMe(updates);
      setSuccess('Profile updated successfully');
      setPassword('');
      loadUserData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Update failed');
    }
  };

  const handleUpgradePlan = async (planId: number) => {
    try {
      await subscriptionApi.upgrade(planId);
      setSuccess('Plan upgraded successfully');
      loadUserData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upgrade failed');
    }
  };

  if (loading) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-muted-foreground">Manage your account and subscription</p>
      </div>

      <Tabs defaultValue="profile" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="subscription">Subscription</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>Update your account details</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                {error && (
                  <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                    {error}
                  </div>
                )}
                {success && (
                  <div className="rounded-md bg-green-50 p-3 text-sm text-green-800">
                    {success}
                  </div>
                )}
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Username</Label>
                  <Input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>New Password (leave empty to keep current)</Label>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter new password"
                  />
                </div>
                <Button type="submit">Update Profile</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscription" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Current Subscription</CardTitle>
              <CardDescription>Your active plan</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-md">
                <p className="text-lg font-semibold">{subscription?.plan_name}</p>
                <p className="text-sm text-muted-foreground">
                  {subscription?.operations_used} / {subscription?.max_operations} operations used
                </p>
                <p className="text-sm text-muted-foreground">
                  {subscription?.operations_remaining} operations remaining
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Available Plans</CardTitle>
              <CardDescription>Upgrade your plan for more operations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {plans.map((plan) => (
                  <div
                    key={plan.id}
                    className={`p-4 border rounded-md ${
                      plan.id === subscription?.plan_id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                  >
                    <h3 className="font-semibold text-lg">{plan.name}</h3>
                    <p className="text-2xl font-bold mt-2">
                      ${(plan.price / 100).toFixed(2)}
                      <span className="text-sm text-muted-foreground">/month</span>
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      {plan.max_operations} operations/month
                    </p>
                    <p className="text-sm mt-2">{plan.description}</p>
                    {plan.id !== subscription?.plan_id && (
                      <Button
                        onClick={() => handleUpgradePlan(plan.id)}
                        className="w-full mt-4"
                        variant={plan.id > (subscription?.plan_id || 0) ? 'default' : 'outline'}
                      >
                        {plan.id > (subscription?.plan_id || 0) ? 'Upgrade' : 'Downgrade'}
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Processing History</CardTitle>
              <CardDescription>Your recent image processing operations</CardDescription>
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No history yet</p>
              ) : (
                <div className="space-y-2">
                  {history.map((record) => (
                    <div key={record.id} className="flex items-center justify-between p-3 border rounded-md">
                      <div>
                        <p className="font-medium">{record.filename}</p>
                        <p className="text-sm text-muted-foreground">
                          Operation: {record.operation} | {record.original_size} → {record.processed_size}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(record.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
