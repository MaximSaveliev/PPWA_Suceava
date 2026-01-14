# Delete Operations Documentation

This document explains the implementation of Hard Delete and Soft Delete operations in the application.

## Exercise 1: Hard Delete (Physical Deletion)

### Entity: ImageRecord

**Implementation Location:**
- Model: `app/models/image_record.py`
- DAL: `app/dal/image_dal.py`
- Service: `app/services/image_service.py`
- Controller: `app/controllers/image_controller.py`

**Why Hard Delete?**
ImageRecord is a history tracking entity that records image processing operations. It can be safely deleted without losing critical application history because:
1. It doesn't affect referential integrity (no other entities depend on it)
2. It's purely for user history tracking
3. Deleting old records helps manage database size
4. Users can delete their own processing history

**Endpoints:**

```http
DELETE /api/v1/images/{image_id}
Authorization: Bearer <token>
```

**Features:**
- Permanently removes the record from the database
- Verifies user ownership before deletion
- Returns 204 No Content on success
- Returns 404 if record not found
- Returns 403 if user doesn't own the record

**Frontend Integration:**
- Location: `frontend/src/app/dashboard/profile/page.tsx`
- Delete button (trash icon) in History tab
- Confirmation dialog before deletion
- Automatically updates UI after deletion

**Code Example:**

```python
# DAL Method
def delete(self, image_record: ImageRecord) -> None:
    """
    Hard delete - permanently removes image record from database.
    Safe to use as this is history tracking and doesn't break referential integrity.
    """
    self.db.delete(image_record)
    self.db.commit()

# Service Method
def delete_image(self, image_id: int, user_id: int) -> None:
    """Hard delete image record - permanently removes from database"""
    image = self.image_dal.get_by_id(image_id)
    
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image record not found")
    
    # Verify ownership
    if image.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    self.image_dal.delete(image)
```

---

## Exercise 2: Soft Delete (Logical Deletion)

### Entity: Plan

**Implementation Location:**
- Model: `app/models/plan.py`
- DAL: `app/dal/plan_dal.py`
- Controller: `app/controllers/plan_controller.py`

**Why Soft Delete?**
Plan entity uses soft delete because:
1. Plans are referenced by Subscription entities (foreign key relationship)
2. Hard deleting a plan would break existing subscription records
3. Historical data needs to be preserved (users who had/have this plan)
4. Plans can be reactivated if needed
5. Maintains data integrity and audit trail

**Database Schema Changes:**

```python
class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False, index=True)
    max_operations = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(Text)
    is_deleted = Column(Boolean, default=False, nullable=False)  # Soft delete flag
    deleted_at = Column(TIMESTAMP, nullable=True)  # Timestamp when deleted
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
```

**Endpoints:**

### Soft Delete
```http
DELETE /api/v1/plans/{plan_id}/soft
Authorization: Bearer <admin_token>
```
Marks the plan as deleted without removing it from the database.

### Restore
```http
POST /api/v1/plans/{plan_id}/restore
Authorization: Bearer <admin_token>
```
Restores a previously soft-deleted plan.

### Hard Delete (Admin Only - Use with Caution)
```http
DELETE /api/v1/plans/{plan_id}/hard
Authorization: Bearer <admin_token>
```
Permanently removes the plan. Will fail if subscriptions reference it.

### Get All Plans
```http
GET /api/v1/plans/?include_deleted=false
```
By default excludes soft-deleted plans. Set `include_deleted=true` to see all.

**Features:**
1. **Automatic Filtering**: All GET operations exclude soft-deleted plans by default
2. **Restore Capability**: Deleted plans can be restored
3. **Timestamp Tracking**: Records when plan was deleted
4. **Referential Integrity**: Prevents breaking existing subscriptions
5. **Admin Only**: Only administrators can delete/restore plans

**DAL Methods:**

```python
def get_by_id(self, plan_id: int, include_deleted: bool = False) -> Optional[Plan]:
    query = self.db.query(Plan).filter(Plan.id == plan_id)
    if not include_deleted:
        query = query.filter(Plan.is_deleted == False)
    return query.first()

def get_all(self, include_deleted: bool = False) -> list[Plan]:
    query = self.db.query(Plan)
    if not include_deleted:
        query = query.filter(Plan.is_deleted == False)
    return query.all()

def soft_delete(self, plan: Plan) -> Plan:
    """Soft delete - marks plan as deleted without removing from database"""
    plan.is_deleted = True
    plan.deleted_at = datetime.utcnow()
    self.db.commit()
    self.db.refresh(plan)
    return plan

def restore(self, plan: Plan) -> Plan:
    """Restore a soft-deleted plan"""
    plan.is_deleted = False
    plan.deleted_at = None
    self.db.commit()
    self.db.refresh(plan)
    return plan

def hard_delete(self, plan: Plan) -> None:
    """Hard delete - physically removes plan from database (use with caution)"""
    self.db.delete(plan)
    self.db.commit()
```

**Updated Operations:**

All retrieval operations now respect the soft delete flag:
- `get_by_id()` - Excludes deleted by default
- `get_by_name()` - Excludes deleted by default
- `get_all()` - Excludes deleted by default
- All methods accept `include_deleted` parameter for admin operations

---

## Frontend Integration

### Image History Delete (Hard Delete)

**Location:** `frontend/src/app/dashboard/profile/page.tsx`

```typescript
const handleDeleteImage = async (imageId: number) => {
  if (!confirm('Are you sure you want to delete this image record? This action cannot be undone.')) return;

  try {
    await imageApi.delete(imageId);
    setHistory(history.filter(img => img.id !== imageId));
    setSuccess('Image record deleted successfully');
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to delete image record');
  }
};
```

**UI Elements:**
- Delete button with trash icon next to each history record
- Confirmation dialog warning about permanent deletion
- Success/error messages
- Automatic UI update after deletion

### Plan Management (Soft Delete) - API Available

**API Methods:** `frontend/src/lib/api.ts`

```typescript
export const planApi = {
  getAll: async (includeDeleted: boolean = false) => {
    const response = await api.get('/plans/', { params: { include_deleted: includeDeleted } });
    return response.data;
  },
  softDelete: async (planId: number) => {
    const response = await api.delete(`/plans/${planId}/soft`);
    return response.data;
  },
  restore: async (planId: number) => {
    const response = await api.post(`/plans/${planId}/restore`);
    return response.data;
  },
  hardDelete: async (planId: number) => {
    await api.delete(`/plans/${planId}/hard`);
  },
};
```

---

## Testing the Implementation

### Test Hard Delete (ImageRecord)

1. **Create some image processing history:**
   - Go to Dashboard → Process Image
   - Upload and process a few images

2. **View history:**
   - Go to Profile → History tab
   - See list of processed images

3. **Delete a record:**
   - Click trash icon on any record
   - Confirm deletion
   - Record should disappear from list

4. **Verify deletion:**
   - Check database - record should be gone
   - Refresh page - record should not reappear

### Test Soft Delete (Plan)

**Via API (Swagger UI or Postman):**

1. **Get all plans:**
   ```
   GET /api/v1/plans/
   ```

2. **Soft delete a plan:**
   ```
   DELETE /api/v1/plans/1/soft
   ```

3. **Verify plan is hidden:**
   ```
   GET /api/v1/plans/
   ```
   Plan should not appear in the list

4. **Get including deleted:**
   ```
   GET /api/v1/plans/?include_deleted=true
   ```
   Plan should appear with `is_deleted: true`

5. **Restore the plan:**
   ```
   POST /api/v1/plans/1/restore
   ```

6. **Verify restoration:**
   ```
   GET /api/v1/plans/
   ```
   Plan should appear again with `is_deleted: false`

---

## Database Migration

To apply the soft delete changes to the Plan table, run this SQL:

```sql
ALTER TABLE plans 
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
ADD COLUMN deleted_at TIMESTAMP NULL;
```

Or use Alembic migration:

```bash
alembic revision --autogenerate -m "Add soft delete to plans"
alembic upgrade head
```

---

## Key Differences: Hard vs Soft Delete

| Aspect | Hard Delete (ImageRecord) | Soft Delete (Plan) |
|--------|---------------------------|-------------------|
| **Data Removal** | Permanent | Reversible |
| **Database** | Record removed | Record remains, flag changed |
| **Referential Integrity** | No impact | Preserved |
| **Audit Trail** | Lost | Maintained |
| **Use Case** | History/logs that can be recreated | Core entities with relationships |
| **Recovery** | Impossible | Can be restored |
| **Query Filter** | Not needed | Required on all queries |
| **Performance** | Frees space | No space freed |

---

## Best Practices

1. **Use Soft Delete when:**
   - Entity has foreign key relationships
   - Historical data must be preserved
   - Compliance/audit requirements exist
   - Recovery might be needed

2. **Use Hard Delete when:**
   - No other entities depend on it
   - Historical data is not critical
   - Database cleanup is needed
   - GDPR/data retention policies require it

3. **Always:**
   - Verify user permissions before deletion
   - Provide confirmation dialogs in UI
   - Log deletion operations
   - Handle errors gracefully
   - Document the deletion type in code comments
