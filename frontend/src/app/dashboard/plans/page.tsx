'use client';

import { useState, useEffect } from 'react';
import { planApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plan } from '@/types';
import { Trash2, RotateCcw, Plus } from 'lucide-react';
import { toast } from 'sonner';

export default function PlansPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDeleted, setShowDeleted] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [planToDelete, setPlanToDelete] = useState<Plan | null>(null);
  const [createDialog, setCreateDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [editingPlan, setEditingPlan] = useState<Plan | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    max_operations: 0,
    price: 0,
    description: ''
  });

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const data = await planApi.getAll(showDeleted);
        setPlans(data);
      } catch (err) {
        toast.error('Failed to load plans', {
          description: err instanceof Error ? err.message : 'An error occurred',
        });
      } finally {
        setLoading(false);
      }
    };
    fetchPlans();
  }, [showDeleted]);

  const loadPlans = async () => {
    try {
      const data = await planApi.getAll(showDeleted);
      setPlans(data);
    } catch (err) {
      toast.error('Failed to load plans', {
        description: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  const handleCreatePlan = async () => {
    try {
      await planApi.create(formData);
      setCreateDialog(false);
      setFormData({ name: '', max_operations: 0, price: 0, description: '' });
      loadPlans();
      toast.success('Plan created successfully');
    } catch (err) {
      toast.error('Failed to create plan', {
        description: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  const handleUpdatePlan = async () => {
    if (!editingPlan) return;

    try {
      await planApi.update(editingPlan.id, formData);
      setEditDialog(false);
      setEditingPlan(null);
      setFormData({ name: '', max_operations: 0, price: 0, description: '' });
      loadPlans();
      toast.success('Plan updated successfully');
    } catch (err) {
      toast.error('Failed to update plan', {
        description: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  const handleSoftDelete = (plan: Plan) => {
    setPlanToDelete(plan);
    setDeleteDialog(true);
  };

  const confirmSoftDelete = async () => {
    if (!planToDelete) return;

    try {
      await planApi.softDelete(planToDelete.id);
      setDeleteDialog(false);
      setPlanToDelete(null);
      loadPlans();
      toast.success('Plan deleted successfully', {
        description: 'The plan has been soft deleted and hidden from users',
      });
    } catch (err) {
      setDeleteDialog(false);
      setPlanToDelete(null);
      toast.error('Failed to delete plan', {
        description: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  const handleRestore = async (planId: number) => {
    try {
      await planApi.restore(planId);
      loadPlans();
      toast.success('Plan restored successfully', {
        description: 'The plan is now active again',
      });
    } catch (err) {
      toast.error('Failed to restore plan', {
        description: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  const openEditDialog = (plan: Plan) => {
    setEditingPlan(plan);
    setFormData({
      name: plan.name,
      max_operations: plan.max_operations,
      price: plan.price,
      description: plan.description || ''
    });
    setEditDialog(true);
  };

  const openCreateDialog = () => {
    setFormData({ name: '', max_operations: 0, price: 0, description: '' });
    setCreateDialog(true);
  };

  if (loading) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Plan Management</h1>
        <p className="text-muted-foreground">Manage subscription plans</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Subscription Plans</CardTitle>
              <CardDescription>Create, edit, and manage plans</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowDeleted(!showDeleted)}
              >
                {showDeleted ? 'Hide Deleted' : 'Show Deleted'}
              </Button>
              <Button onClick={openCreateDialog}>
                <Plus className="h-4 w-4 mr-2" />
                Create Plan
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Max Operations</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {plans.map((plan) => (
                <TableRow key={plan.id} className={plan.is_deleted ? 'opacity-50' : ''}>
                  <TableCell>{plan.id}</TableCell>
                  <TableCell className="font-medium">{plan.name}</TableCell>
                  <TableCell>{plan.max_operations}</TableCell>
                  <TableCell>${plan.price.toFixed(2)}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {plan.description || 'No description'}
                  </TableCell>
                  <TableCell>
                    {plan.is_deleted ? (
                      <span className="px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
                        Deleted
                      </span>
                    ) : (
                      <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                        Active
                      </span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      {!plan.is_deleted ? (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openEditDialog(plan)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleSoftDelete(plan)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </>
                      ) : (
                        <Button
                          variant="default"
                          size="sm"
                          onClick={() => handleRestore(plan.id)}
                          className="bg-green-600 hover:bg-green-700 text-white"
                        >
                          <RotateCcw className="h-4 w-4 mr-2" />
                          Restore
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={deleteDialog} onOpenChange={setDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Plan</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the plan &quot;{planToDelete?.name}&quot;? 
              This will soft delete the plan, hiding it from users but preserving existing subscriptions.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmSoftDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={createDialog} onOpenChange={setCreateDialog}>
        <DialogContent className="sm:max-w-[550px] px-6">
          <DialogHeader className="space-y-3 pb-4">
            <DialogTitle className="text-2xl font-semibold">Create New Plan</DialogTitle>
            <DialogDescription className="text-base">Add a new subscription plan</DialogDescription>
          </DialogHeader>
          <div className="grid gap-6 py-2 px-1">
            <div className="grid gap-3">
              <Label htmlFor="name" className="text-sm font-semibold text-gray-900">
                Plan Name
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., PREMIUM"
                className="h-11 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="max_operations" className="text-sm font-semibold text-gray-900">
                Max Operations
              </Label>
              <Input
                id="max_operations"
                type="number"
                value={formData.max_operations}
                onChange={(e) => setFormData({ ...formData, max_operations: parseInt(e.target.value) || 0 })}
                placeholder="e.g., 1000"
                className="h-11 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="price" className="text-sm font-semibold text-gray-900">
                Price ($)
              </Label>
              <Input
                id="price"
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                placeholder="e.g., 29.99"
                className="h-11 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="description" className="text-sm font-semibold text-gray-900">
                Description
              </Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Plan description"
                className="h-11 text-base"
              />
            </div>
          </div>
          <DialogFooter className="gap-2 pt-4">
            <Button variant="outline" onClick={() => setCreateDialog(false)} className="h-10">
              Cancel
            </Button>
            <Button onClick={handleCreatePlan} className="h-10">
              Create Plan
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={editDialog} onOpenChange={setEditDialog}>
        <DialogContent className="sm:max-w-[550px] px-6">
          <DialogHeader className="space-y-3 pb-4">
            <DialogTitle className="text-2xl font-semibold">Edit Plan</DialogTitle>
            <DialogDescription className="text-base">Update plan details</DialogDescription>
          </DialogHeader>
          <div className="grid gap-6 py-2 px-1">
            <div className="grid gap-3">
              <Label htmlFor="edit-name" className="text-sm font-semibold text-gray-900">
                Plan Name
              </Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., PREMIUM"
                className="h-11 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="edit-max_operations" className="text-sm font-semibold text-gray-900">
                Max Operations
              </Label>
              <Input
                id="edit-max_operations"
                type="number"
                value={formData.max_operations}
                onChange={(e) => setFormData({ ...formData, max_operations: parseInt(e.target.value) || 0 })}
                placeholder="e.g., 1000"
                className="h-11 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="edit-price" className="text-sm font-semibold text-gray-900">
                Price ($)
              </Label>
              <Input
                id="edit-price"
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                placeholder="e.g., 29.99"
                className="h-11 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="edit-description" className="text-sm font-semibold text-gray-900">
                Description
              </Label>
              <Input
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Plan description"
                className="h-11 text-base"
              />
            </div>
          </div>
          <DialogFooter className="gap-2 pt-4">
            <Button variant="outline" onClick={() => setEditDialog(false)} className="h-10">
              Cancel
            </Button>
            <Button onClick={handleUpdatePlan} className="h-10">
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
