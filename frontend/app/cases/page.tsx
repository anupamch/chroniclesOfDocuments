'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  CircularProgress,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import ListAltIcon from '@mui/icons-material/ListAlt';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { useRouter, usePathname } from 'next/navigation';
import Layout from '@/components/Layout';
import { getCasesPaginated, Case } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function DashboardPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading: authLoading } = useAuth();
  const [recentCases, setRecentCases] = useState<Case[]>([]);
  const [totalCases, setTotalCases] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && user) {
      fetchDashboardData();
    }
  }, [authLoading, user, pathname]);

  const fetchDashboardData = async () => {
    try {
      // Fetch first page of recent cases for the dashboard
      const data = await getCasesPaginated(1, 6);
      setRecentCases(data.cases);
      setTotalCases(data.total);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewCase = () => {
    router.push('/cases/new');
  };

  const handleViewCase = (caseId: string) => {
    router.push(`/cases/${caseId}`);
  };

  const handleViewAllCases = () => {
    router.push('/cases/list');
  };

  const totalDocuments = Array.isArray(recentCases)
    ? recentCases.reduce((sum, c) => sum + (c.total_documents || 0), 0)
    : 0;

  const activeCases = Array.isArray(recentCases)
    ? recentCases.filter((c) => c.status === 'active').length
    : 0;

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Overview of your document analysis cases
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleNewCase}
            sx={{ textTransform: 'none', borderRadius: 2 }}
          >
            New Case
          </Button>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={4}>
            <Paper
              sx={{
                p: 3,
                textAlign: 'center',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
              }}
              elevation={0}
            >
              <FolderIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700 }}>{totalCases}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Cases
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper
              sx={{
                p: 3,
                textAlign: 'center',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
              }}
              elevation={0}
            >
              <DescriptionIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700 }}>{totalDocuments}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Documents
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper
              sx={{
                p: 3,
                textAlign: 'center',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
              }}
              elevation={0}
            >
              <TrendingUpIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'success.main' }}>
                {activeCases}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Cases
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Recent Cases */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Recent Cases
          </Typography>
          <Button
            variant="text"
            endIcon={<ListAltIcon />}
            onClick={handleViewAllCases}
            sx={{ textTransform: 'none' }}
          >
            View All Cases
          </Button>
        </Box>

        <Grid container spacing={3}>
          {Array.isArray(recentCases) && recentCases.length > 0 ? (
            recentCases.map((caseItem) => (
              <Grid item xs={12} md={6} lg={4} key={caseItem.case_id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    transition: 'box-shadow 0.2s, transform 0.2s',
                    '&:hover': {
                      boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                  elevation={0}
                >
                  <CardActionArea
                    onClick={() => handleViewCase(caseItem.case_id)}
                    sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                        <Typography 
                          variant="subtitle1" 
                          sx={{ 
                            fontWeight: 600, 
                            fontFamily: 'monospace',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            maxWidth: '150px'
                          }}
                        >
                          {caseItem.case_number}
                        </Typography>
                        <Chip
                          label={caseItem.status}
                          size="small"
                          color="success"
                          sx={{ textTransform: 'capitalize' }}
                        />
                      </Box>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          mb: 1, 
                          fontWeight: 500,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {caseItem.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          mb: 2,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                        }}
                      >
                        {caseItem.description || 'No description'}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <Chip
                          icon={<DescriptionIcon />}
                          label={`${caseItem.total_documents || 0} docs`}
                          size="small"
                          variant="outlined"
                        />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(caseItem.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 2 }} elevation={0} variant="outlined">
                <FolderIcon sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No cases yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Create your first case to get started
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleNewCase}
                  sx={{ textTransform: 'none' }}
                >
                  New Case
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      </Box>
    </Layout>
  );
}
