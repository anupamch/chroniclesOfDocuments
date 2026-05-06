import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, ActivityIndicator, TouchableOpacity, Share, Alert, Clipboard } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { getCase, Case } from '../../../lib/api';

export default function TimelineScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [caseDetails, setCaseDetails] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchCaseDetails();
  }, [id]);

  const fetchCaseDetails = async () => {
    try {
      const data = await getCase(id);
      setCaseDetails(data);
    } catch (error) {
      console.error('Fetch case details error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    if (!caseDetails?.timeline_story) return;
    try {
      await Share.share({
        title: `Timeline Analysis: ${caseDetails.case_number}`,
        message: caseDetails.timeline_story,
      });
    } catch (error) {
      console.error('Share error:', error);
    }
  };

  const handleDownload = async () => {
    if (!caseDetails?.timeline_story) return;

    try {
      // Copy timeline story to clipboard
      Clipboard.setString(caseDetails.timeline_story);
      Alert.alert('Success', 'Timeline story copied to clipboard. You can now paste it into any app or save it as a file.');
    } catch (error) {
      console.error('Download error:', error);
      Alert.alert('Error', 'Failed to copy timeline story');
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  if (!caseDetails?.timeline_story) {
    return (
      <View style={styles.centered}>
        <Ionicons name="analytics-outline" size={64} color="#ccc" />
        <Text style={styles.noReportText}>No analysis report available yet.</Text>
        <Text style={styles.subText}>Please upload documents and tap "Analyze" on the case details screen.</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.caseNumber}>{caseDetails.case_number}</Text>
          <Text style={styles.title}>Timeline Analysis</Text>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.shareButton} onPress={handleDownload}>
            <Ionicons name="download-outline" size={24} color="#2196F3" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
            <Ionicons name="share-outline" size={24} color="#2196F3" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.scrollPadding}>
        <View style={styles.reportCard}>
          <Text style={styles.reportText}>{caseDetails.timeline_story}</Text>
        </View>

        {/* Legal Advice Button */}
        <TouchableOpacity
          style={styles.legalAdviceButton}
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
          <Ionicons name="hammer" size={20} color="#fff" />
          <Text style={styles.legalAdviceButtonText}>Get Legal Advice</Text>
        </TouchableOpacity>

        <View style={styles.footer}>
          <Ionicons name="shield-checkmark" size={16} color="#4CAF50" />
          <Text style={styles.footerText}>AI-Generated Analysis Report</Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  caseNumber: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#2196F3',
    textTransform: 'uppercase',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  shareButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerActions: {
    flexDirection: 'row',
    gap: 8,
  },
  content: {
    flex: 1,
  },
  scrollPadding: {
    padding: 20,
    paddingBottom: 40,
  },
  reportCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#f0f0f0',
  },
  reportText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 28,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
    gap: 8,
  },
  legalAdviceButton: {
    backgroundColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 10,
    marginTop: 20,
  },
  legalAdviceButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  noReportText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginTop: 20,
    textAlign: 'center',
  },
  subText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 24,
  },
  backButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    backgroundColor: '#2196F3',
    borderRadius: 8,
  },
  backButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});
