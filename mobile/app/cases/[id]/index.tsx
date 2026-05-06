import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, TouchableOpacity, Image, Alert, ActivityIndicator, Linking } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { getCase, getCaseDocuments, uploadDocument, startScan, getScanStatus, deleteDocument, deleteCase, Case, Document as CaseDocument, WS_URL, getDocumentViewUrl } from '../../../lib/api';

export default function CaseDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [caseDetails, setCaseDetails] = useState<Case | null>(null);
  const [documents, setDocuments] = useState<CaseDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const router = useRouter();

  useEffect(() => {
    fetchCaseDetails();

    // Establish WebSocket connection for real-time updates
    if (id && id !== 'new') {
      const clientId = `mobile_${Math.random().toString(36).substr(2, 9)}`;
      const socket = new WebSocket(`${WS_URL}/${clientId}`);

      // Store socket reference globally for cleanup during deletion
      (global as any).currentSocket = socket;

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WS Mobile] Received:', data);

          if (data.type === 'scan_complete' && data.case_id === id) {
            Alert.alert('Analysis Complete', 'Your timeline report has been updated!');
            // Update local state to reflect completion
            setCaseDetails(prev => prev ? { ...prev, analysis_status: 'completed', timeline_story: prev.timeline_story } : null);
            fetchCaseDetails();
          } else if (data.type === 'document_processed' && data.case_id === id) {
            // Silently refresh documents to update status dots
            getCaseDocuments(id).then(docs => setDocuments(docs.documents));
          }
        } catch (e) {
          console.error('[WS Mobile] Error parsing message:', e);
        }
      };

      socket.onerror = (e) => {
        console.error('[WS Mobile] Error:', e);
      };

      socket.onclose = (e) => {
        console.log('[WS Mobile] Connection closed:', e.code, e.reason);
        // Clear global reference when closed
        (global as any).currentSocket = null;
      };

      return () => {
        console.log('[WS Mobile] Cleanup: closing socket');
        socket.close();
        (global as any).currentSocket = null;
      };
    }
  }, [id]);

  const fetchCaseDetails = async () => {
    if (!id || id === 'new') return;
    
    try {
      const [caseData, docsData] = await Promise.all([
        getCase(id),
        getCaseDocuments(id)
      ]);
      setCaseDetails(caseData);
      setDocuments(docsData.documents);
    } catch (error: any) {
      console.error('Fetch case details error:', error);
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return 'document-text';
    if (type.includes('image')) return 'image';
    return 'document';
  };

  const handleStartScan = async () => {
    if (!caseDetails || caseDetails.total_documents === 0) {
      Alert.alert('No Documents', 'Please upload at least one document before starting analysis.');
      return;
    }

    if (caseDetails.analysis_status === 'in_progress') {
      Alert.alert('Analysis In Progress', 'An analysis is already running for this case.');
      return;
    }

    setScanning(true);
    try {
      await startScan(id);
      // Update local state immediately
      setCaseDetails(prev => prev ? { ...prev, analysis_status: 'in_progress' } : null);
      Alert.alert('Analysis Started', 'The system is now analyzing your documents. This may take a moment.');
    } catch (error: any) {
      console.error('Scan error:', error);
      Alert.alert('Error', error.message);
    } finally {
      setScanning(false);
    }
  };

  const handleCapture = async () => {
    // Request permissions
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission denied', 'We need camera permissions to capture documents');
      return;
    }

    // Launch camera
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      const asset = result.assets[0];
      await handleUpload(asset.uri);
    }
  };

  const handlePickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      const asset = result.assets[0];
      await handleUpload(asset.uri);
    }
  };

  const handleViewDocument = async (docId: string) => {
    try {
      const token = await AsyncStorage.getItem('token');
      const url = `${getDocumentViewUrl(id, docId)}?token=${token}&download=true`;
      await Linking.openURL(url);
    } catch (error) {
      console.error('Error opening document:', error);
      Alert.alert('Error', 'Could not open document');
    }
  };

  const handleDeleteCase = () => {
    Alert.alert(
      'Delete Case',
      'Are you sure you want to delete this case and all its documents?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: async () => {
            try {
              console.log('Starting case deletion for:', id);
              
              // Close WebSocket connection before deletion
              // This prevents any interference during the delete operation
              const socket = (global as any).currentSocket;
              if (socket && socket.readyState === WebSocket.OPEN) {
                console.log('Closing WebSocket connection before deletion');
                socket.close();
              }
              
              // Perform deletion
              console.log('Calling deleteCase API');
              await deleteCase(id);
              console.log('Case deletion successful');
              
              // Navigate away immediately after successful deletion
              router.replace('/(tabs)');
            } catch (error: any) {
              console.error('Delete case error:', error);
              
              // Better error handling
              let errorMessage = 'Failed to delete case';
              
              if (error.response) {
                console.log('Error response:', error.response.status, error.response.data);
                errorMessage = error.response.data?.detail || error.response.data?.message || `Server error: ${error.response.status}`;
              } else if (error.request) {
                console.log('No response received:', error.request);
                errorMessage = 'Network error - please check your connection';
              } else {
                console.log('Error message:', error.message);
                errorMessage = error.message || 'Unknown error occurred';
              }
              
              Alert.alert('Error', errorMessage);
            }
          }
        }
      ]
    );
  };

  const handleDeleteDocument = (docId: string) => {
    Alert.alert(
      'Delete Document',
      'Are you sure you want to delete this document?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteDocument(id, docId);
              fetchCaseDetails(); // Refresh
            } catch (error: any) {
              Alert.alert('Error', error.message);
            }
          }
        }
      ]
    );
  };

  const handleUpload = async (uri: string) => {
    setUploading(true);
    try {
      const fileName = `doc_${Date.now()}.jpg`;
      await uploadDocument(id, uri, fileName);
      Alert.alert('Success', 'Document uploaded successfully');
      fetchCaseDetails(); // Refresh
    } catch (error: any) {
      console.error('Upload error:', error);
      Alert.alert('Upload Failed', error.message);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  if (!caseDetails) return null;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.caseNumber} numberOfLines={1}>{caseDetails.case_number}</Text>
        <Text style={styles.title}>{caseDetails.title}</Text>
        <Text style={styles.description}>{caseDetails.description || 'No description'}</Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statBox}>
          <Text style={styles.statLabel}>Documents</Text>
          <Text style={styles.statValue}>{caseDetails.total_documents || 0}</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statLabel}>Status</Text>
          <Text style={styles.statValue}>{caseDetails.status}</Text>
        </View>
      </View>

      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>Document Management</Text>

        <View style={styles.primaryActions}>
          <TouchableOpacity
            style={[
              styles.primaryButton,
              (scanning || caseDetails.total_documents === 0 || caseDetails.analysis_status === 'in_progress') && styles.buttonDisabled
            ]}
            onPress={handleStartScan}
            disabled={scanning || caseDetails.total_documents === 0 || caseDetails.analysis_status === 'in_progress'}
          >
            <Ionicons name="analytics" size={24} color="#fff" />
            <Text style={styles.primaryButtonText}>
              {caseDetails.analysis_status === 'in_progress' ? 'Analysis in Progress...' : scanning ? 'Analyzing...' : 'Start AI Analysis'}
            </Text>
          </TouchableOpacity>

          {caseDetails.timeline_story && (
            <TouchableOpacity
              style={styles.timelineButton}
              onPress={() => router.push(`/cases/${id}/timeline`)}
            >
              <Ionicons name="journal" size={24} color="#2196F3" />
              <Text style={styles.timelineButtonText}>View Timeline Report</Text>
            </TouchableOpacity>
          )}

          {caseDetails.timeline_story && (
            <TouchableOpacity
              style={styles.legalButton}
              onPress={() => router.push({
                pathname: `/cases/${id}/legalAdvice`,
                params: {
                  id: id!,
                  caseNumber: caseDetails.case_number,
                  caseTitle: caseDetails.title,
                  timelineStory: caseDetails.timeline_story || ''
                }
              })}
            >
              <Ionicons name="hammer" size={24} color="#fff" />
              <Text style={styles.legalButtonText}>Get Legal Advice</Text>
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.secondaryActions}>
          <Text style={styles.subsectionTitle}>Add Documents</Text>
          <View style={styles.actionButtons}>
            <TouchableOpacity style={styles.actionButton} onPress={handleCapture} disabled={uploading || scanning}>
              <View style={[styles.iconCircle, { backgroundColor: '#E3F2FD' }]}>
                <Ionicons name="camera" size={32} color="#2196F3" />
              </View>
              <Text style={styles.actionText}>Camera</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton} onPress={handlePickImage} disabled={uploading || scanning}>
              <View style={[styles.iconCircle, { backgroundColor: '#F3E5F5' }]}>
                <Ionicons name="images" size={32} color="#9C27B0" />
              </View>
              <Text style={styles.actionText}>Gallery</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.documentsSection}>
          <Text style={styles.subsectionTitle}>Case Documents ({documents.length})</Text>
          {documents.length > 0 ? (
            <View style={styles.documentList}>
              {documents.map((doc) => (
                <View key={doc.document_id} style={styles.documentItem}>
                  <View style={[styles.docIconContainer, { backgroundColor: doc.file_type.includes('image') ? '#F3E5F5' : '#E3F2FD' }]}>
                    <Ionicons 
                      name={getFileIcon(doc.file_type) as any} 
                      size={24} 
                      color={doc.file_type.includes('image') ? '#9C27B0' : '#2196F3'} 
                    />
                  </View>
                  <View style={styles.docInfo}>
                    <Text style={styles.docName} numberOfLines={1}>{doc.file_name}</Text>
                    <Text style={styles.docMeta}>
                      {formatFileSize(doc.file_size)} • {new Date(doc.uploaded_at).toLocaleDateString()}
                    </Text>
                  </View>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                    <TouchableOpacity 
                      onPress={() => handleViewDocument(doc.document_id)}
                      style={styles.viewIcon}
                    >
                      <Ionicons name="download-outline" size={20} color="#2196F3" />
                    </TouchableOpacity>
                    <TouchableOpacity 
                      onPress={() => handleDeleteDocument(doc.document_id)}
                      style={styles.viewIcon}
                    >
                      <Ionicons name="trash-outline" size={18} color="#FF5252" />
                    </TouchableOpacity>
                  </View>
                  <View style={[styles.statusDot, { backgroundColor: doc.status === 'completed' ? '#4CAF50' : '#FFC107' }]} />
                </View>
              ))}
            </View>
          ) : (
            <View style={styles.emptyDocs}>
              <Ionicons name="document-outline" size={48} color="#eee" />
              <Text style={styles.emptyDocsText}>No documents uploaded yet</Text>
            </View>
          )}
        </View>

        <View style={styles.dangerZone}>
          <TouchableOpacity 
            style={styles.deleteCaseButton}
            onPress={handleDeleteCase}
          >
            <Ionicons name="trash-outline" size={20} color="#FF5252" />
            <Text style={styles.deleteCaseText}>Delete Case</Text>
          </TouchableOpacity>
        </View>
      </View>

      {(uploading || scanning) && (
        <View style={styles.uploadingOverlay}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.uploadingText}>
            {uploading ? 'Uploading document...' : 'Processing analysis...'}
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    padding: 20,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  caseNumber: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 4,
    flexShrink: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#666',
    lineHeight: 22,
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 20,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#f9f9f9',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#eee',
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a1a1a',
    textTransform: 'capitalize',
  },
  actionsContainer: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 20,
  },
  primaryActions: {
    gap: 12,
    marginBottom: 32,
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  buttonDisabled: {
    backgroundColor: '#A5D6A7',
    elevation: 0,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  timelineButton: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 10,
    borderWidth: 2,
    borderColor: '#2196F3',
  },
  timelineButtonText: {
    color: '#2196F3',
    fontSize: 16,
    fontWeight: 'bold',
  },
  legalButton: {
    backgroundColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 10,
  },
  legalButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  secondaryActions: {
    backgroundColor: '#f9f9f9',
    padding: 20,
    borderRadius: 16,
    marginBottom: 24,
  },
  subsectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 16,
  },
  documentsSection: {
    marginTop: 8,
  },
  documentList: {
    gap: 12,
  },
  documentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#f0f0f0',
  },
  docIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  docInfo: {
    flex: 1,
  },
  docName: {
    fontSize: 15,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  docMeta: {
    fontSize: 12,
    color: '#999',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginLeft: 8,
  },
  emptyDocs: {
    alignItems: 'center',
    padding: 40,
    backgroundColor: '#fafafa',
    borderRadius: 12,
    borderStyle: 'dashed',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  emptyDocsText: {
    marginTop: 8,
    fontSize: 14,
    color: '#bbb',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 20,
  },
  actionButton: {
    alignItems: 'center',
  },
  iconCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  actionText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  uploadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  uploadingText: {
    color: '#fff',
    marginTop: 16,
    fontSize: 16,
    fontWeight: 'bold',
  },
  viewIcon: {
    padding: 8,
    marginRight: 4,
  },
  dangerZone: {
    margin: 20,
    marginTop: 10,
    marginBottom: 40,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  deleteCaseButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FF5252',
    backgroundColor: '#FFF5F5',
    gap: 8,
  },
  deleteCaseText: {
    color: '#FF5252',
    fontSize: 16,
    fontWeight: '600',
  },
});
