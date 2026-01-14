'use client';

import { useState, useEffect } from 'react';
import { userApi, subscriptionApi, imageApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { User, Plan, Subscription, ImageRecord } from '@/types';
import { Trash2 } from 'lucide-react';
import { toast } from 'sonner';

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

  const [deleteDialog, setDeleteDialog] = useState(false);
  const [imageToDelete, setImageToDelete] = useState<number | null>(null);
  const [imageViewDialog, setImageViewDialog] = useState(false);
  const [selectedImage, setSelectedImage] = useState<ImageRecord | null>(null);
  const [imageBlobUrls, setImageBlobUrls] = useState<{[key: number]: string}>({});

  useEffect(() => {
    loadUserData();
  }, []);

  useEffect(() => {
    const loadImages = async () => {
      const urls: {[key: number]: string} = {};
      for (const record of history) {
        try {
          const blob = await imageApi.getImage(record.id);
          urls[record.id] = URL.createObjectURL(blob);
        } catch (err) {
          console.error(`Failed to load image ${record.id}`);
        }
      }
      setImageBlobUrls(urls);
    };
    if (history.length > 0) {
      loadImages();
    }
    return () => {
      Object.values(imageBlobUrls).forEach(url => URL.revokeObjectURL(url));
    };
  }, [history]);

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
      
      // Sort plans: FREE, BASIC, PREMIUM, ENTERPRISE
      const planOrder = ['FREE', 'BASIC', 'PREMIUM', 'ENTERPRISE'];
      const sortedPlans = plansData.sort((a: Plan, b: Plan) => {
        const aIndex = planOrder.indexOf(a.name.toUpperCase());
        const bIndex = planOrder.indexOf(b.name.toUpperCase());
        return (aIndex === -1 ? 999 : aIndex) - (bIndex === -1 ? 999 : bIndex);
      });
      setPlans(sortedPlans);
      
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
      toast.success('Plan upgraded successfully');
      loadUserData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Upgrade failed');
    }
  };

  const handleDeleteImage = async (imageId: number) => {
    setImageToDelete(imageId);
    setDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (!imageToDelete) return;

    try {
      await imageApi.delete(imageToDelete);
      setHistory(history.filter(img => img.id !== imageToDelete));
      setDeleteDialog(false);
      setImageToDelete(null);
      toast.success('Image deleted successfully', {
        description: 'The image record has been removed from your history',
      });
    } catch (err: any) {
      setDeleteDialog(false);
      setImageToDelete(null);
      toast.error('Failed to delete image', {
        description: err.response?.data?.detail || 'An error occurred while deleting the image',
      });
    }
  };

  const cancelDelete = () => {
    setDeleteDialog(false);
    setImageToDelete(null);
  };

  const handleViewImage = (record: ImageRecord) => {
    setSelectedImage(record);
    setImageViewDialog(true);
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
                    className={`p-6 border-2 rounded-lg transition-all ${
                      plan.id === subscription?.plan_id 
                        ? 'border-blue-500 bg-blue-50 shadow-md' 
                        : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-xl">{plan.name}</h3>
                      {plan.id === subscription?.plan_id && (
                        <span className="px-3 py-1 bg-blue-500 text-white text-xs rounded-full font-medium">
                          Current
                        </span>
                      )}
                    </div>
                    <div className="mb-4">
                      <p className="text-3xl font-bold text-gray-900">
                        ${(plan.price / 100).toFixed(2)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        per month
                      </p>
                    </div>
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm">
                        <span className="font-semibold text-gray-700">
                          {plan.max_operations.toLocaleString()}
                        </span>
                        <span className="text-muted-foreground ml-1">operations/month</span>
                      </div>
                      <p className="text-sm text-gray-600">{plan.description}</p>
                    </div>
                    {plan.id !== subscription?.plan_id && (
                      <Button
                        onClick={() => handleUpgradePlan(plan.id)}
                        className="w-full"
                        variant={plan.id > (subscription?.plan_id || 0) ? 'default' : 'outline'}
                      >
                        {plan.id > (subscription?.plan_id || 0) ? 'Upgrade Plan' : 'Switch Plan'}
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
                    <div key={record.id} className="flex items-center gap-4 p-3 border rounded-md hover:bg-gray-50 transition-colors">
                      <div 
                        className="shrink-0 w-16 h-16 rounded border bg-gray-100 overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={() => handleViewImage(record)}
                      >
                        {imageBlobUrls[record.id] ? (
                          <img 
                            src={imageBlobUrls[record.id]}
                            alt={record.filename}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#999" strokeWidth="2">
                              <rect x="3" y="3" width="18" height="18" rx="2"></rect>
                              <circle cx="8.5" cy="8.5" r="1.5"></circle>
                              <path d="M21 15l-5-5L5 21"></path>
                            </svg>
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate" title={record.filename}>
                          {record.filename.length > 40 
                            ? record.filename.substring(0, 40) + '...' 
                            : record.filename}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Operation: {record.operation} | {record.original_size} → {record.processed_size}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(record.created_at).toLocaleString()}
                        </p>
                      </div>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteImage(record.id)}
                        className="shrink-0"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={deleteDialog} onOpenChange={setDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Image Record</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this image record? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={cancelDelete}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={imageViewDialog} onOpenChange={setImageViewDialog}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] w-auto h-auto p-0 overflow-hidden">
          <div className="relative w-full h-full flex flex-col">
            <DialogHeader className="px-6 pt-6 pb-4 shrink-0">
              <DialogTitle>{selectedImage?.filename}</DialogTitle>
              <DialogDescription>
                {selectedImage?.operation} | {selectedImage?.original_size} → {selectedImage?.processed_size}
              </DialogDescription>
            </DialogHeader>
            <div className="flex items-center justify-center bg-gray-50 px-6 pb-6 overflow-hidden min-h-0 flex-1">
              {selectedImage && imageBlobUrls[selectedImage.id] ? (
                <img 
                  src={imageBlobUrls[selectedImage.id]}
                  alt={selectedImage.filename}
                  className="object-contain"
                  style={{maxHeight: '80vh', maxWidth: '100%', width: 'auto', height: 'auto'}}
                />
              ) : (
                <div className="flex items-center justify-center h-64">
                  <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="#999" strokeWidth="1">
                    <rect x="3" y="3" width="18" height="18" rx="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <path d="M21 15l-5-5L5 21"></path>
                  </svg>
                </div>
              )}
            </div>
            <DialogFooter className="px-6 pb-6 shrink-0">
              <Button onClick={() => setImageViewDialog(false)}>
                Close
              </Button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
