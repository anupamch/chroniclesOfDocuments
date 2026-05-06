import { Stack } from 'expo-router';
import { AuthProvider } from '../context/AuthContext';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <AuthProvider>
      <StatusBar style="auto" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="login" options={{ title: 'Login' }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="cases/new" options={{ 
          headerShown: true, 
          title: 'New Case',
          headerBackTitle: 'Back'
        }} />
        <Stack.Screen name="cases/[id]/index" options={{ 
          headerShown: true, 
          title: 'Case Details',
          headerBackTitle: 'Back'
        }} />
        <Stack.Screen name="cases/[id]/timeline" options={{ 
          headerShown: true, 
          title: 'Timeline Analysis',
          headerBackTitle: 'Back'
        }} />
      </Stack>
    </AuthProvider>
  );
}
