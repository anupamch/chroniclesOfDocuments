import React, { useState } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, ActivityIndicator, Alert, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { createCase } from '../../lib/api';

export default function NewCaseScreen() {
  const [caseNumber, setCaseNumber] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleCreate = async () => {
    if (!caseNumber || !title) {
      Alert.alert('Error', 'Case Number and Title are required');
      return;
    }

    // Validate case number format (alphanumeric, hyphens, underscores only)
    const caseNumberRegex = /^[a-zA-Z0-9\-_]+$/;
    if (!caseNumberRegex.test(caseNumber)) {
      Alert.alert('Error', 'Case number can only contain letters, numbers, hyphens (-), and underscores (_). Spaces are not allowed.');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Creating case with data:', {
        case_number: caseNumber,
        title: title,
        description: description,
      });
      
      const newCase = await createCase({
        case_number: caseNumber,
        title: title,
        description: description,
      });
      
      console.log('Case created successfully:', newCase);
      Alert.alert('Success', 'Case created successfully');
      router.replace(`/cases/${newCase.case_id}`);
    } catch (error: any) {
      console.error('Create case error:', error);
      
      // Better error handling
      let errorMessage = 'Failed to create case';
      
      if (error.response) {
        // Server responded with error status
        console.log('Error response:', error.response.status, error.response.data);
        
        // Handle validation errors specifically
        if (error.response.status === 422) {
          const detail = error.response.data?.detail;
          if (Array.isArray(detail) && detail.length > 0) {
            // Extract specific validation error messages
            const validationErrors = detail.map(err => {
              if (err.msg && err.loc) {
                const field = err.loc[err.loc.length - 1]; // Get the field name
                return `${field}: ${err.msg}`;
              }
              return err.msg || 'Validation error';
            });
            errorMessage = validationErrors.join('\n');
          } else if (typeof detail === 'string') {
            errorMessage = detail;
          } else {
            errorMessage = `Validation error: ${error.response.status}`;
          }
        } else {
          errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`;
        }
      } else if (error.request) {
        // Request was made but no response received
        console.log('No response received:', error.request);
        errorMessage = 'Network error - please check your connection';
      } else {
        // Something else happened
        console.log('Error message:', error.message);
        errorMessage = error.message || 'Unknown error occurred';
      }
      
      Alert.alert('Error', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 100 : 0}
    >
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.headerTitle}>Create New Case</Text>

        <View style={styles.form}>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Case Number *</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. CASE-2024-001"
            value={caseNumber}
            onChangeText={setCaseNumber}
            autoCapitalize="characters"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Case Title *</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. Document Analysis for Project X"
            value={title}
            onChangeText={setTitle}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Description</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder="Optional case details..."
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />
        </View>

        <TouchableOpacity 
          style={[styles.button, isLoading && styles.buttonDisabled]} 
          onPress={handleCreate}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Create Case</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.cancelButton}
          onPress={() => router.back()}
          disabled={isLoading}
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 24,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 32,
  },
  form: {
    gap: 20,
  },
  inputGroup: {
    gap: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  input: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    height: 120,
  },
  button: {
    backgroundColor: '#2196F3',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 12,
  },
  buttonDisabled: {
    backgroundColor: '#90CAF9',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cancelButton: {
    padding: 16,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
  },
});
