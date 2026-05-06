import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { Redirect } from 'expo-router';

export default function TabLayout() {
  const { user, loading } = useAuth();

  if (loading) return null;
  
  if (!user) {
    return <Redirect href="/login" />;
  }

  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#2196F3' }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Cases',
          tabBarIcon: ({ color }) => <Ionicons name="folder" size={24} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color }) => <Ionicons name="person" size={24} color={color} />,
        }}
      />
    </Tabs>
  );
}
