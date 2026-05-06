'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { getUsers, deleteUser, User } from '@/lib/api';
import { 
  Container, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Button,
  Chip,
  CircularProgress,
  Box,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import Layout from '@/components/Layout';
import { register } from '@/lib/api';

export default function AdminUsersPage() {
  const { user, loading } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  
  // Create User State
  const [open, setOpen] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newPhoneNumber, setNewPhoneNumber] = useState('');
  const [newRole, setNewRole] = useState('customer');
  const [createError, setCreateError] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const fetchUsers = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch users');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!loading && user?.role === 'admin') {
      fetchUsers();
    }
  }, [user, loading]);

  const handleOpenDialog = () => {
    setOpen(true);
    setCreateError('');
    setNewEmail('');
    setNewPassword('');
    setNewFullName('');
    setNewPhoneNumber('');
    setNewRole('customer');
  };

  const handleCloseDialog = () => {
    if (isCreating) return;
    setOpen(false);
  };

  const handleCreateUser = async () => {
    setCreateError('');
    
    if (!newEmail || !newPassword || !newFullName) {
      setCreateError('Please fill in all fields');
      return;
    }

    // Password validation
    if (newPassword.length < 8) {
      setCreateError('Password must be at least 8 characters long');
      return;
    }

    if (!/\d/.test(newPassword)) {
      setCreateError('Password must contain at least one number');
      return;
    }

    setIsCreating(true);
    try {
      await register({
        email: newEmail,
        password: newPassword,
        full_name: newFullName,
        phone_number: newPhoneNumber,
        role: newRole
      });
      setOpen(false);
      fetchUsers();
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async (userId: string) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    setDeletingId(userId);
    try {
      await deleteUser(userId);
      await fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeletingId(null);
    }
  };

  if (loading || isLoading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  if (user?.role !== 'admin') {
    return (
      <Layout>
        <Alert severity="error" sx={{ mt: 4 }}>
          You do not have permission to view this page.
        </Alert>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            User Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
          >
            Create User
          </Button>
        </Box>
        
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        
        <TableContainer component={Paper} elevation={2}>
          <Table>
            <TableHead sx={{ backgroundColor: 'background.default' }}>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Joined</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((u) => (
                <TableRow key={u.user_id}>
                  <TableCell>{u.full_name}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>
                    <Chip 
                      label={u.role} 
                      color={u.role === 'admin' ? 'secondary' : 'primary'} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{new Date(u.created_at).toLocaleDateString()}</TableCell>
                  <TableCell align="right">
                    <Button
                      variant="outlined"
                      color="error"
                      size="small"
                      startIcon={deletingId === u.user_id ? <CircularProgress size={16} /> : <DeleteIcon />}
                      onClick={() => handleDelete(u.user_id)}
                      disabled={deletingId === u.user_id || u.user_id === user?.user_id}
                    >
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No users found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={open} onClose={handleCloseDialog} maxWidth="xs" fullWidth>
          <DialogTitle>Create New User</DialogTitle>
          <DialogContent>
            {createError && <Alert severity="error" sx={{ mb: 2, mt: 1 }}>{createError}</Alert>}
            <TextField
              margin="dense"
              label="Full Name"
              fullWidth
              variant="outlined"
              value={newFullName}
              onChange={(e) => setNewFullName(e.target.value)}
              sx={{ mb: 2, mt: 1 }}
            />
            <TextField
              margin="dense"
              label="Phone Number"
              fullWidth
              variant="outlined"
              value={newPhoneNumber}
              onChange={(e) => setNewPhoneNumber(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Email Address"
              type="email"
              fullWidth
              variant="outlined"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Password"
              type="password"
              fullWidth
              variant="outlined"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              helperText="At least 8 chars and 1 number"
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mt: 1 }}>
              <InputLabel id="role-label">Role</InputLabel>
              <Select
                labelId="role-label"
                value={newRole}
                label="Role"
                onChange={(e) => setNewRole(e.target.value)}
              >
                <MenuItem value="customer">Customer</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button onClick={handleCloseDialog} disabled={isCreating}>Cancel</Button>
            <Button 
              onClick={handleCreateUser} 
              variant="contained" 
              disabled={isCreating}
            >
              {isCreating ? <CircularProgress size={24} /> : 'Create User'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Layout>
  );
}
