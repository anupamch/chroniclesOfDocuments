import React, { useState } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { login, loginWithEmailOrPhone } from '../lib/api';
import { useRouter } from 'expo-router';

export default function LoginScreen() {
  const [identifier, setIdentifier] = useState('9073436357'); // Default for testing phone
  const [password, setPassword] = useState('A@123456');
  const [isLoading, setIsLoading] = useState(false);
  const { loginState } = useAuth();
  const router = useRouter();

  // Auto-detect email vs phone number
  const detectIdentifierType = (value: string): 'email' | 'phone' | 'unknown' => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const phoneRegex = /^[\+]?[0-9]{10,15}$/;
    
    if (emailRegex.test(value)) return 'email';
    if (phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) return 'phone';
    return 'unknown';
  };

  const handleLogin = async () => {
    if (!identifier || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    const identifierType = detectIdentifierType(identifier);
    
    if (identifierType === 'unknown') {
      Alert.alert('Error', 'Please enter a valid email address or phone number');
      return;
    }

    setIsLoading(true);
    try {
      let data;
      if (identifierType === 'email') {
        data = await login({ email: identifier, password });
      } else {
        data = await loginWithEmailOrPhone({ phone_number: identifier, password });
      }
      await loginState(data.access_token);
    } catch (error: any) {
      console.error('Login error:', error);
      
      // Provide specific error messages based on the error
      let errorMessage = 'Login failed';
      if (error.message) {
        if (error.message.includes('Incorrect email or password')) {
          errorMessage = 'Invalid email or password';
        } else if (error.message.includes('Incorrect phone number or password')) {
          errorMessage = 'Invalid phone number or password';
        } else if (error.message.includes('Inactive user')) {
          errorMessage = 'Your account has been deactivated';
        } else if (error.message.includes('network')) {
          errorMessage = 'Network error. Please check your connection';
        } else {
          errorMessage = error.message;
        }
      }
      
      Alert.alert('Login Failed', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1 }}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer} keyboardShouldPersistTaps="handled">
        <View style={styles.container}>
          <View style={styles.card}>
            <Text style={styles.title}>Chronicles of Documents</Text>
            <Text style={styles.subtitle}>Sign in to continue</Text>

            <TextInput
              style={styles.input}
              placeholder="Email Address or Phone Number"
              value={identifier}
              onChangeText={setIdentifier}
              autoCapitalize="none"
              keyboardType="email-address"
              autoComplete="username"
            />

            <TextInput
              style={styles.input}
              placeholder="Password"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />

            <TouchableOpacity 
              style={[styles.button, isLoading && styles.buttonDisabled]} 
              onPress={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Sign In</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.linkButton} 
              onPress={() => router.push('/register')}
            >
              <Text style={styles.linkText}>
                Don't have an account? <Text style={styles.linkHighlight}>Sign Up</Text>
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    flexGrow: 1,
  },
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 32,
  },
  input: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#2196F3',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    backgroundColor: '#90CAF9',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  linkButton: {
    marginTop: 24,
    alignItems: 'center',
  },
  linkText: {
    color: '#666',
    fontSize: 14,
  },
  linkHighlight: {
    color: '#2196F3',
    fontWeight: 'bold',
  },
});
