# Testing Delete Operations

## Hard Delete (ImageRecord) - Available in UI ✅

**Location:** Dashboard → Profile → History Tab

**How to Test:**
1. Login to the application
2. Process some images (Dashboard → Process Image)
3. Go to Profile → History tab
4. Click the trash icon on any image record
5. A custom dialog popup will appear asking for confirmation
6. Click "Delete" to confirm (or "Cancel" to abort)
7. **Toast notification** appears at the bottom showing "Image deleted successfully"
8. Image record is permanently deleted from database
9. List updates automatically

**UI Features:**
- ✅ Custom styled dialog popup (not browser alert)
- ✅ Confirmation dialog before delete
- ✅ **Toast notification** for success/error (not dialog popup)
- ✅ Automatic list update
- ✅ Error handling with toast notifications

---

## Soft Delete (Plan) - NOW AVAILABLE IN UI ✅

**Location:** Dashboard → Plans (Admin Only)

**How to Test in UI:**
1. Login as admin user
2. Click "Plans" in the navigation menu
3. View all active plans in the table
4. Click "Show Deleted" to see soft-deleted plans too

### Soft Delete a Plan:
1. Click the trash icon next to any active plan
2. Confirmation dialog appears
3. Click "Delete" to confirm
4. Toast notification: "Plan deleted successfully"
5. Plan is marked as deleted (is_deleted = true)
6. Plan row appears with "Deleted" badge and reduced opacity

### Restore a Deleted Plan:
1. Click "Show Deleted" button
2. Find deleted plans (marked with red "Deleted" badge)
3. Click "Restore" button
4. Toast notification: "Plan restored successfully"
5. Plan is restored (is_deleted = false)
6. Plan appears in active listings again

### Create/Edit Plans:
1. Click "Create Plan" button
2. Fill in the form (Name, Max Operations, Price, Description)
3. Click "Create Plan"
4. Toast notification confirms creation
5. Click "Edit" on any plan to modify its details

**UI Features:**
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Soft delete with confirmation dialog
- ✅ One-click restore for deleted plans
- ✅ Toggle to show/hide deleted plans
- ✅ Toast notifications for all operations
- ✅ Visual indicators (badges, opacity) for deleted items
- ✅ Admin-only access

---

## Delete in Admin Dashboard (Users) - NOW AVAILABLE ✅

**Location:** Dashboard → Admin → Users Tab

**How to Test:**
1. Login as admin
2. Go to Admin panel
3. Find a non-admin user in the table
4. Click the trash icon
5. Custom dialog popup appears: "Are you sure you want to delete user [username]?"
6. Click "Delete" to confirm (or "Cancel" to abort)
7. **Toast notification** appears: "User deleted successfully"
8. User is permanently removed from database

**UI Features:**
- ✅ Custom dialog confirmation (not browser alert)
- ✅ Toast notifications for success/error
- ✅ Cannot delete admin users (button disabled)
- ✅ Clear error messages

---

### Testing with Swagger UI

1. **Open Swagger UI:**
   ```
   http://localhost:8000/docs
   ```

2. **Login as Admin:**
   - Go to `/api/v1/auth/login` endpoint
   - Click "Try it out"
   - Enter admin credentials:
     ```json
     {
       "username": "admin_username",
       "password": "admin_password"
     }
     ```
   - Copy the `access_token` from response
   - Click "Authorize" button at top
   - Paste token as: `Bearer YOUR_TOKEN_HERE`
   - Click "Authorize"

3. **View All Plans:**
   ```
   GET /api/v1/plans/
   ```
   - Shows only active (non-deleted) plans by default
   - Add `?include_deleted=true` to see deleted plans too

4. **Soft Delete a Plan:**
   ```
   DELETE /api/v1/plans/{plan_id}/soft
   ```
   - Example: DELETE /api/v1/plans/1/soft
   - Plan is marked as deleted (is_deleted = true)
   - Plan data remains in database
   - Existing subscriptions are NOT affected

5. **Verify Soft Delete:**
   ```
   GET /api/v1/plans/
   ```
   - Deleted plan should NOT appear in list
   
   ```
   GET /api/v1/plans/?include_deleted=true
   ```
   - Deleted plan SHOULD appear with is_deleted: true

6. **Restore Deleted Plan:**
   ```
   POST /api/v1/plans/{plan_id}/restore
   ```
   - Example: POST /api/v1/plans/1/restore
   - Plan is restored (is_deleted = false)
   - Plan appears in normal listings again

7. **Hard Delete Plan (Dangerous!):**
   ```
   DELETE /api/v1/plans/{plan_id}/hard
   ```
   - Permanently removes plan from database
   - Will FAIL if subscriptions reference this plan
   - Use soft delete instead!

### Testing with Postman/cURL

**1. Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

**2. Get Plans:**
```bash
curl -X GET "http://localhost:8000/api/v1/plans/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**3. Soft Delete:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/plans/1/soft" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**4. Restore:**
```bash
curl -X POST "http://localhost:8000/api/v1/plans/1/restore" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Database Verification

### Check Soft Delete in Database

```sql
-- See all plans including deleted
SELECT id, name, price, is_deleted, deleted_at, created_at 
FROM plans;

-- See only active plans
SELECT id, name, price, is_deleted, deleted_at, created_at 
FROM plans 
WHERE is_deleted = false;

-- See only deleted plans
SELECT id, name, price, is_deleted, deleted_at, created_at 
FROM plans 
WHERE is_deleted = true;
```

### Check Image Records (Hard Delete)

```sql
-- See user's image history
SELECT id, filename, operation, created_at 
FROM image_records 
WHERE user_id = 1
ORDER BY created_at DESC;

-- After hard delete, record will be completely gone
```

---

## Key Differences in UI

### Hard Delete (Images)
- **Before:** Browser `confirm()` alert - plain, ugly
- **After:** Custom styled dialog with proper buttons
- **Success:** Toast notification at bottom (not popup dialog)
- **Experience:** Modern, clean, professional

### Soft Delete (Plans)
- **Before:** Only via API (Swagger/Postman)
- **After:** Full UI in Dashboard → Plans
- **Access:** Admin-only with navigation link
- **Features:** Create, Edit, Soft Delete, Restore, Show/Hide deleted
- **Success:** Toast notifications for all operations

### Delete Users (Admin)
- **Before:** Browser `confirm()` alert
- **After:** Custom styled dialog with proper buttons
- **Success:** Toast notification (not inline message)
- **Protection:** Cannot delete admin users

---

## Testing Checklist

### Hard Delete (Image Records) ✅
- [x] Image appears in history
- [x] Click delete button shows confirmation dialog
- [x] Dialog has Cancel and Delete buttons
- [x] Cancel closes dialog without deleting
- [x] Delete removes record and shows toast
- [x] Toast notification appears at bottom
- [x] List updates automatically
- [x] Database record is gone

### Soft Delete (Plans) ✅
- [x] Plans page accessible from admin navigation
- [x] Table shows active plans by default
- [x] "Show Deleted" toggle works
- [x] Delete button shows confirmation dialog
- [x] Soft delete marks plan as deleted
- [x] Deleted plan has "Deleted" badge
- [x] Deleted plan has reduced opacity
- [x] Restore button appears for deleted plans
- [x] Restore makes plan active again
- [x] Toast notifications show for all operations
- [x] Create/Edit forms work properly

### Delete Users (Admin) ✅
- [x] Dere do I see toast notifications?**
A: Toast notifications appear at the bottom-right of the screen for a few seconds. They show success messages (green) or errors (red).

**Q: How do I access the Plans management page?**
A: Login as an admin user. You'll see a "Plans" link in the top navigation menu. Click it to manage plans.

**Q: Can I see deleted plans?**
A: Yes! In the Plans page, click the "Show Deleted" button to toggle visibility of soft-deleted plans.

**Q: Can regular users delete plans?**
A: No. Only admin users can access the Plans page and perform delete/restore operations.

**Q: What's the difference between soft delete and hard delete?**
A: 
- **Soft Delete:** Sets is_deleted=true, hides from listings, but data stays in database. Used for Plans to preserve subscriptions.
- **Hard Delete:** Permanently removes record from database. Used for ImageRecords that don't affect other data.

**Q: Why use toast instead of dialog for success messages?**
A: Toasts are less intrusive - they appear briefly and disappear automatically. Dialogs require user interaction to close. Toasts are better for simple notifications.

**Q: Can I restore a deleted plan?**
A: Yes! Click "Show Deleted" in the Plans page, find the deleted plan, and click the "Restore" button
- [x] Toast notification appears
- [x] Admin users cannot be deleted (button disabled)
- [x] List updates automatically

### API Operations (Backend) ✅
- [x] GET /plans/ excludes deleted plans
- [x] DELETE /plans/{id}/soft marks plan as deleted
- [x] Deleted plan has is_deleted = true
- [x] Deleted plan has deleted_at timestamp
- [x] GET /plans/?include_deleted=true shows deleted plans
- [x] Deleted plan doesn't break existing subscriptions
- [x] POST /plans/{id}/restore restores plan
- [x] Restored plan has is_deleted = false

---

## Common Questions

**Q: Why isn't soft delete in the UI?**
A: Plans are critical system data, typically managed by administrators through API or admin panel. Regular users shouldn't delete/restore plans.

**Q: Can I add plan management UI?**
A: Yes! You can create an admin-only page with plan CRUD operations. The API endpoints are ready.

**Q: What happens to subscriptions when plan is soft deleted?**
A: Nothing! Existing subscriptions continue working. That's why we use soft delete - to preserve data integrity.

**Q: When should I use hard delete for plans?**
A: Almost never! Only if you're absolutely sure no subscriptions reference it and you need to clean up test data.

**Q: Can users see deleted plans?**
A: No. The API automatically filters them out unless explicitly requested with `include_deleted=true`.
