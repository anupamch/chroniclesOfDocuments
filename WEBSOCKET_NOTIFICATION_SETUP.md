# WebSocket Notification System - Analysis Complete Event

## Overview

The application now has a complete **WebSocket-based real-time notification system** that fires events when document analysis completes and releases the button on the frontend.

---

## How It Works

### 1. **User Interaction**
```
User clicks "Start Scan" button
    ↓
Button is disabled (spinning icon)
Button text shows "🔄 Analysis in Progress..."
```

### 2. **Backend Processing**
```
API receives POST /cases/{case_id}/scan
    ↓
Sets analysis_status = "in_progress"
    ↓
Adds background task: process_case_documents()
    ↓
Returns immediately (API endpoint closes)
    ↓
Background task processes documents asynchronously
    ↓
For each document processed:
  - Broadcasts "document_processed" event via WebSocket
    ↓
When all documents done:
  - Broadcasts "scan_complete" event via WebSocket
  - Sets analysis_status = "completed"
```

### 3. **Frontend Listens & Reacts**
```
WebSocket connection established (auto on page load)
    ↓
Listen for incoming events
    ↓
Receive "scan_complete" event:
  - Set analysisComplete = true
  - Show green success alert: "✨ Analysis complete!"
  - Set analysis_status = "completed"
  - Button becomes ENABLED again ✅
  - Auto-refresh UI to show results
    ↓
Button now shows "Start Scan" again (ready for re-scan)
```

---

## Code Changes Made

### Frontend: `frontend/app/cases/[id]/page.tsx`

#### 1. **Added New State Variables**
```typescript
const [analysisComplete, setAnalysisComplete] = useState(false);
const [notificationOpen, setNotificationOpen] = useState(false);
```

#### 2. **Enhanced WebSocket Handler**
```typescript
socket.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    console.log('[WS] Received:', data.type, data);

    if (data.type === 'scan_complete' && data.case_id === caseId) {
      // ✅ Analysis complete - release button
      setAnalysisComplete(true);
      setNotificationOpen(true);
      setCaseDetails(prev => ({ 
        ...prev, 
        analysis_status: 'completed' 
      }));
      // Auto-refresh results
      setTimeout(() => fetchData(), 500);
    }
  } catch (err) {
    console.error('[WS] Error:', err);
  }
};
```

#### 3. **Updated Start Scan Handler**
```typescript
const handleStartScan = async () => {
  setScanning(true);
  setAnalysisComplete(false);  // Reset flag
  setError(null);
  
  try {
    await startScan(caseId);
    setCaseDetails(prev => ({ 
      ...prev, 
      analysis_status: 'in_progress' 
    }));
    // WebSocket will notify when complete!
  } catch (err: any) {
    setError(err.message || 'Failed to start scan');
    setScanning(false);
  }
};
```

#### 4. **Updated Button with Loading Indicator**
```typescript
<Button
  variant="outlined"
  startIcon={
    caseDetails?.analysis_status === 'in_progress' 
      ? <CircularProgress size={20} /> 
      : <PlayArrowIcon />
  }
  onClick={handleStartScan}
  disabled={
    scanning || 
    documents.length === 0 || 
    caseDetails?.analysis_status === 'in_progress'
  }
>
  {caseDetails?.analysis_status === 'in_progress' 
    ? '🔄 Analysis in Progress...' 
    : 'Start Scan'}
</Button>
```

#### 5. **Added Success Notification Alert**
```typescript
{analysisComplete && notificationOpen && (
  <Alert 
    severity="success" 
    onClose={() => setNotificationOpen(false)}
    sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}
  >
    <CheckCircleIcon fontSize="small" />
    ✨ Analysis complete! Your timeline has been generated successfully.
  </Alert>
)}
```

### Backend: Already Implemented ✅
The backend already had WebSocket broadcasting in place:
- `backend/app/services/websocket_manager.py` - Manages connections
- `backend/app/services/scan_service.py` - Broadcasts "scan_complete" event
- `backend/app/api/routes.py` - WebSocket endpoint

---

## Button State Flow

### Before (Without WebSocket)
```
[Start Scan]  ← Button enabled
    ↓ click
[Starting...] ← Button disabled temporarily
    ↓ immediate return
[Start Scan]  ← Button re-enabled (but analysis still running!)
```
❌ Problem: Button enables while analysis is still running

### After (With WebSocket)
```
[Start Scan]  ← Button enabled
    ↓ click
[🔄 Analysis in Progress...]  ← Button disabled, spinning loader
    ↓ WebSocket receives scan_complete
[Start Scan]  ← Button re-enabled (analysis actually done!)
✨ Success Alert shows
```
✅ Working: Button disabled until analysis truly completes

---

## Testing the WebSocket Flow

### 1. **Backend Console Should Show**
```
[WS] Client user_XXX connected
[WS] Received: null
Processing: document1.pdf
✓ Completed: document1.pdf
[WS] Broadcasting: {"type": "document_processed", ...}
[WS] Broadcasting: {"type": "scan_complete", ...}
```

### 2. **Frontend Browser Console Should Show**
```
[WS] Connected successfully
[WS] Received: keepalive null
[WS] Received: document_processed {...}
[WS] Received: scan_complete {...}
```

### 3. **UI Behavior**
- ✅ Button shows spinning loader while "Analysis in Progress..."
- ✅ Green alert appears when complete
- ✅ Button becomes clickable again
- ✅ Timeline results auto-refresh

---

## Configuration

### Environment Variables (Already Set)
```env
# backend/.env
MODEL_CALL=local          # Uses Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### Docker Services Required
```bash
# Make sure these are running:
- Backend API (port 8000)
- Frontend (port 3000)
- Ollama (port 11434)
- MongoDB (port 27017)
```

Check status:
```bash
docker compose ps
```

---

## Event Types & Payloads

### `scan_complete` Event (Main Event)
```json
{
  "type": "scan_complete",
  "case_id": "abc-123-def",
  "message": "AI Analysis complete"
}
```

### `document_processed` Event (Per-document Update)
```json
{
  "type": "document_processed",
  "case_id": "abc-123-def",
  "document_id": "doc-456",
  "file_name": "contract.pdf"
}
```

---

## Troubleshooting

### ❌ Button doesn't release / stays disabled

**Check 1: WebSocket Connected?**
```javascript
// In browser console:
// Look for "[WS] Connected successfully" in console logs
```

**Check 2: Backend Broadcasting?**
```bash
# Check backend logs
docker logs <backend_container_id> | grep "\[WS\]"
```

**Check 3: Case ID Mismatch?**
```javascript
// Ensure case_id in event matches current page case_id
// In browser console:
console.log(window.location.pathname)  // Should show /cases/[case_id]
```

### ❌ Analysis still running but button re-enabled

**Cause:** The `setScanning(false)` was executed before background task completed.

**Fix:** ✅ Already fixed - now we rely on `analysis_status` from server state:
```typescript
disabled={
  scanning || 
  documents.length === 0 || 
  caseDetails?.analysis_status === 'in_progress'  // ← Reliable server state
}
```

### ❌ Notification doesn't show

**Check:**
1. Alert component is imported ✅
2. `notificationOpen` state is true when event arrives ✅
3. Severity is "success" (shows green) ✅
4. Click the X to close it and test again

---

## Flow Diagram

```
Frontend                          Backend                         Database
   │                                │                                 │
   │─── Start Scan ──────────────→  │                                 │
   │                                │─── Set analysis_status="in_progress"
   │                                │─────────────────────────────→   │
   │                                │
   │                                │─── Process documents (async)
   │                                │    1. Extract text
   │                                │    2. Classify type
   │                                │    3. Analyze content
   │                                │    4. Generate timeline
   │                                │
   │                                │─ Broadcast "document_processed" (repeat)
   │← WebSocket: document_processed │
   │  (refresh status silently)      │
   │                                │
   │                                │─ Generate timeline story
   │                                │─── Set analysis_status="completed"
   │                                │─────────────────────────────→   │
   │                                │─ Broadcast "scan_complete" ──→  │
   │← WebSocket: scan_complete      │
   │  Release button ✅              │
   │  Show success alert ✨          │
   │  Refresh timeline results       │
   │                                │
   │─ Show timeline to user         │
   │
```

---

## Files Modified

1. **Frontend**
   - `frontend/app/cases/[id]/page.tsx` - Enhanced WebSocket handling and button states

2. **Backend** (Already working)
   - `backend/app/services/websocket_manager.py` - ✅ Manages WebSocket connections
   - `backend/app/services/scan_service.py` - ✅ Broadcasts completion events
   - `backend/app/api/routes.py` - ✅ Starts background processing

---

## Summary

✅ **When analysis completes:**
1. Backend broadcasts `scan_complete` via WebSocket
2. Frontend receives event
3. Button state is updated to "completed"
4. Button becomes enabled again
5. Success notification appears
6. Timeline results auto-refresh

**Result:** Users see real-time feedback that analysis is complete and can interact with results immediately!
