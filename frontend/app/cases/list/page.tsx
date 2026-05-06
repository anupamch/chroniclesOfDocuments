'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import DescriptionIcon from '@mui/icons-material/Description';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import DeleteIcon from '@mui/icons-material/Delete';
import { useRouter, usePathname } from 'next/navigation';
import Layout from '@/components/Layout';
import { getCasesPaginated, Case, deleteCase } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

type SortOrder = 'asc' | 'desc';

interface Column {
  id: string;
  label: string;
  align?: 'left' | 'center' | 'right';
  sortable: boolean;
}

const columns: Column[] = [
  { id: 'case_number', label: 'Case Number', sortable: true },
  { id: 'title', label: 'Title', sortable: true },
  { id: 'description', label: 'Description', sortable: true },
  { id: 'total_documents', label: 'Documents', align: 'center', sortable: true },
  { id: 'status', label: 'Status', align: 'center', sortable: true },
  { id: 'created_at', label: 'Created', sortable: true },
  { id: 'actions', label: 'Actions', align: 'center', sortable: false },
];

export default function CaseListPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading: authLoading } = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [totalCases, setTotalCases] = useState(0);
  const [page, setPage] = useState(0); // MUI TablePagination is 0-indexed
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const fetchCases = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      // Backend API is 1-indexed, MUI TablePagination is 0-indexed
      const data = await getCasesPaginated(
        page + 1,
        rowsPerPage,
        search || undefined,
        undefined,
        sortBy,
        sortOrder
      );
      // Filter out deleted cases as an additional safety measure
      const activeCases = data.cases.filter(caseItem => caseItem.status !== 'deleted');
      setCases(activeCases);
      setTotalCases(data.total);
    } catch (error) {
      console.error('Failed to fetch cases:', error);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, search, sortBy, sortOrder, user]);

  useEffect(() => {
    if (!authLoading && user) {
      fetchCases();
    }
  }, [authLoading, user, fetchCases, pathname]);

  const handleDeleteCase = async (caseId: string) => {
    if (!window.confirm('Are you sure you want to delete this case? All associated documents will be permanently deleted.')) {
      return;
    }
    
    setDeletingId(caseId);
    try {
      await deleteCase(caseId);
      // Fetch cases again to update list
      fetchCases();
    } catch (error) {
      console.error('Failed to delete case:', error);
      alert('Failed to delete case');
    } finally {
      setDeletingId(null);
    }
  };

  const handleSort = (columnId: string) => {
    if (sortBy === columnId) {
      // Toggle direction
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(columnId);
      setSortOrder('asc');
    }
    setPage(0);
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearch = () => {
    setSearch(searchInput);
    setPage(0);
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setSearch('');
    setPage(0);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleViewCase = (caseId: string) => {
    router.push(`/cases/${caseId}`);
  };

  const handleNewCase = () => {
    router.push('/cases/new');
  };

  const getStatusColor = (status: string): 'success' | 'warning' | 'default' | 'error' => {
    switch (status) {
      case 'active': return 'success';
      case 'closed': return 'warning';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  return (
    <Layout>
      <Box>
        {/* Page Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Case List
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleNewCase}
            sx={{ textTransform: 'none', borderRadius: 2 }}
          >
            New Case
          </Button>
        </Box>

        {/* Search Bar */}
        <Paper
          sx={{
            p: 2,
            mb: 3,
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            borderRadius: 2,
          }}
          elevation={0}
          variant="outlined"
        >
          <TextField
            id="case-search-input"
            size="small"
            placeholder="Search by case number, title, or description..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={handleKeyDown}
            sx={{
              flex: 1,
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
              endAdornment: searchInput && (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={handleClearSearch}>
                    <ClearIcon fontSize="small" />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            sx={{ textTransform: 'none', borderRadius: 2, px: 3 }}
          >
            Search
          </Button>
          {search && (
            <Chip
              label={`Results for "${search}"`}
              onDelete={handleClearSearch}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </Paper>

        {/* Cases Table */}
        <Paper sx={{ borderRadius: 2, overflow: 'hidden' }} elevation={0} variant="outlined">
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow
                  sx={{
                    backgroundColor: 'primary.main',
                    '& .MuiTableCell-head': {
                      color: 'white',
                      fontWeight: 600,
                      fontSize: '0.8rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      py: 1.5,
                    },
                  }}
                >
                  {columns.map((col) => (
                    <TableCell key={col.id} align={col.align || 'left'}>
                      {col.sortable ? (
                        <TableSortLabel
                          active={sortBy === col.id}
                          direction={sortBy === col.id ? sortOrder : 'asc'}
                          onClick={() => handleSort(col.id)}
                          sx={{
                            color: 'white !important',
                            '&.Mui-active': {
                              color: 'white !important',
                            },
                            '& .MuiTableSortLabel-icon': {
                              color: 'rgba(255,255,255,0.7) !important',
                            },
                          }}
                        >
                          {col.label}
                        </TableSortLabel>
                      ) : (
                        col.label
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                      <CircularProgress size={32} />
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Loading cases...
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : cases.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                      <DescriptionIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                      <Typography variant="body1" color="text.secondary">
                        {search ? `No cases found matching "${search}"` : 'No cases yet'}
                      </Typography>
                      {!search && (
                        <Button
                          variant="outlined"
                          startIcon={<AddIcon />}
                          onClick={handleNewCase}
                          sx={{ mt: 2, textTransform: 'none' }}
                        >
                          Create First Case
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  cases.map((caseItem, index) => (
                    <TableRow
                      key={caseItem.case_id}
                      hover
                      onClick={() => handleViewCase(caseItem.case_id)}
                      sx={{
                        cursor: 'pointer',
                        backgroundColor: index % 2 === 0 ? 'transparent' : 'grey.50',
                        '&:hover': {
                          backgroundColor: 'action.hover',
                        },
                        '&:last-child td, &:last-child th': { border: 0 },
                      }}
                    >
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            color: 'primary.main',
                            fontFamily: 'monospace',
                          }}
                        >
                          {caseItem.case_number}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500, maxWidth: 250 }} noWrap>
                          {caseItem.title}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            maxWidth: 300,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {caseItem.description || '—'}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          icon={<DescriptionIcon sx={{ fontSize: '14px !important' }} />}
                          label={caseItem.total_documents || 0}
                          size="small"
                          variant="outlined"
                          sx={{ fontWeight: 500 }}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={caseItem.status}
                          size="small"
                          color={getStatusColor(caseItem.status)}
                          sx={{ textTransform: 'capitalize', fontWeight: 500 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(caseItem.created_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                          <Tooltip title="View Case Details">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleViewCase(caseItem.case_id);
                              }}
                              color="primary"
                            >
                              <OpenInNewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Case">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteCase(caseItem.case_id);
                              }}
                              color="error"
                              disabled={deletingId === caseItem.case_id}
                            >
                              {deletingId === caseItem.case_id ? (
                                <CircularProgress size={20} color="inherit" />
                              ) : (
                                <DeleteIcon fontSize="small" />
                              )}
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <TablePagination
            component="div"
            count={totalCases}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25, 50]}
            sx={{
              borderTop: '1px solid',
              borderColor: 'divider',
              '& .MuiTablePagination-toolbar': {
                px: 2,
              },
            }}
          />
        </Paper>
      </Box>
    </Layout>
  );
}
