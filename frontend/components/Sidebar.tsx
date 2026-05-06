'use client';

import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Tooltip,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ListAltIcon from '@mui/icons-material/ListAlt';
import GavelIcon from '@mui/icons-material/Gavel';
import { useRouter, usePathname } from 'next/navigation';

import { useAuth } from '@/context/AuthContext';
import PersonIcon from '@mui/icons-material/Person';
import PeopleIcon from '@mui/icons-material/People';
import LogoutIcon from '@mui/icons-material/Logout';

interface SidebarProps {
  open: boolean;
}

export default function Sidebar({ open }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const getMenuItems = () => {
    if (!user) return [];

    const items = [
      {
        label: 'Dashboard',
        icon: <DashboardIcon />,
        path: '/cases',
      },
      {
        label: 'Case List',
        icon: <ListAltIcon />,
        path: '/cases/list',
      },
      {
        label: 'Legal Advice',
        icon: <GavelIcon />,
        path: '/legal',
      },
    ];

    if (user.role === 'admin') {
      items.push({
        label: 'User Management',
        icon: <PeopleIcon />,
        path: '/admin/users',
      });
    }

    items.push({
      label: 'Profile',
      icon: <PersonIcon />,
      path: '/profile',
    });

    return items;
  };

  const menuItems = getMenuItems();

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Menu Header */}
      {open && (
        <Box sx={{ px: 2, pt: 2, pb: 1 }}>
          <Typography
            variant="overline"
            sx={{
              fontWeight: 700,
              fontSize: '0.65rem',
              letterSpacing: '0.1em',
              color: 'text.secondary',
            }}
          >
            NAVIGATION
          </Typography>
        </Box>
      )}

      {/* Navigation Menu */}
      <List sx={{ px: 1, pt: open ? 0 : 1 }}>
        {menuItems.map((item) => {
          const isActive = pathname === item.path;

          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <Tooltip title={open ? '' : item.label} placement="right" arrow>
                <ListItemButton
                  selected={isActive}
                  onClick={() => router.push(item.path)}
                  sx={{
                    borderRadius: 1.5,
                    minHeight: 44,
                    justifyContent: open ? 'initial' : 'center',
                    px: 2,
                    '&.Mui-selected': {
                      backgroundColor: 'primary.main',
                      color: 'white',
                      '&:hover': {
                        backgroundColor: 'primary.dark',
                      },
                      '& .MuiListItemIcon-root': {
                        color: 'white',
                      },
                    },
                    '&:hover': {
                      backgroundColor: isActive ? 'primary.dark' : 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: open ? 2 : 'auto',
                      justifyContent: 'center',
                      color: isActive ? 'white' : 'primary.main',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {open && (
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontSize: '0.875rem',
                        fontWeight: isActive ? 600 : 500,
                      }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            </ListItem>
          );
        })}
        
        {user && (
          <ListItem disablePadding sx={{ mb: 0.5 }}>
            <Tooltip title={open ? '' : 'Logout'} placement="right" arrow>
              <ListItemButton
                onClick={logout}
                sx={{
                  borderRadius: 1.5,
                  minHeight: 44,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2,
                  '&:hover': {
                    backgroundColor: 'error.light',
                    color: 'white',
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 2 : 'auto',
                    justifyContent: 'center',
                    color: 'error.main',
                  }}
                >
                  <LogoutIcon color="inherit" />
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="Logout"
                    primaryTypographyProps={{
                      fontSize: '0.875rem',
                      fontWeight: 500,
                      color: 'error.main',
                    }}
                  />
                )}
              </ListItemButton>
            </Tooltip>
          </ListItem>
        )}
      </List>

      <Divider sx={{ mt: 1 }} />

      {/* Spacer to push content down */}
      <Box sx={{ flexGrow: 1 }} />

      {/* Footer */}
      {open && (
        <>
          <Divider />
          <Box sx={{ p: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
              Chronicles of Documents
            </Typography>
          </Box>
        </>
      )}
    </Box>
  );
}
