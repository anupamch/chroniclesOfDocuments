import React, { useState } from 'react';
import { StyleSheet, View, Text, ScrollView, TouchableOpacity, TextInput, ActivityIndicator, Alert, Share } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { getLegalAdvice, downloadLegalAdvice, LegalAdviceResponse } from '../../../lib/api';

export default function LegalAdviceScreen() {
  const { id, caseNumber, caseTitle, timelineStory } = useLocalSearchParams<{
    id: string;
    caseNumber: string;
    caseTitle: string;
    timelineStory: string;
  }>();

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LegalAdviceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<'pdf' | 'doc' | null>(null);
  const router = useRouter();

  const handleDownload = async (format: 'pdf' | 'doc') => {
    if (!result) return;

    setDownloading(format);
    try {
      const fileUri = await downloadLegalAdvice(
        result,
        format,
        caseNumber,
        caseTitle
      );

      // Offer to share the file
      Alert.alert(
        'Download Complete',
        `Your legal advice has been saved as ${format.toUpperCase()}. Would you like to share it?`,
        [
          { text: 'OK', style: 'cancel' },
          {
            text: 'Share',
            onPress: async () => {
              try {
                await Share.share({
                  url: fileUri,
                  title: `Legal Advice - ${caseNumber || 'Case'}`
                });
              } catch (shareError) {
                console.error('Share error:', shareError);
              }
            }
          }
        ]
      );
    } catch (err: any) {
      console.error('Download error:', err);
      Alert.alert('Download Failed', err.message || 'Failed to download document');
    } finally {
      setDownloading(null);
    }
  };

  const handleGetAdvice = async () => {
    if (!query.trim()) {
      Alert.alert('Required', 'Please enter your legal question');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await getLegalAdvice(
        query,
        'en',
        timelineStory || undefined,
        caseNumber,
        caseTitle
      );
      setResult(response);
    } catch (err: any) {
      console.error('Legal advice error:', err);
      setError(err.message || 'Failed to get legal advice');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResult(null);
    setError(null);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#2196F3" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Legal Advice</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentPadding}>
        {!result ? (
          <>
            <Text style={styles.label}>Your Legal Question</Text>
            <TextInput
              style={styles.textInput}
              multiline
              numberOfLines={4}
              placeholder="Describe your legal concern or question about this case..."
              value={query}
              onChangeText={setQuery}
              editable={!loading}
            />

            {error && (
              <View style={styles.errorContainer}>
                <Ionicons name="alert-circle" size={20} color="#FF5252" />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            <View style={styles.buttonRow}>
              <TouchableOpacity
                style={[styles.button, styles.secondaryButton]}
                onPress={handleClear}
                disabled={loading}
              >
                <Text style={styles.secondaryButtonText}>Clear</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.button, styles.primaryButton, (!query.trim() || loading) && styles.buttonDisabled]}
                onPress={handleGetAdvice}
                disabled={loading || !query.trim()}
              >
                {loading ? (
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <>
                    <Ionicons name="gavel" size={20} color="#fff" />
                    <Text style={styles.primaryButtonText}>Get Advice</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>

            {/* Sample Questions */}
            <View style={styles.samplesContainer}>
              <Text style={styles.samplesTitle}>Sample Questions</Text>
              {[
                'What legal options do I have based on this case?',
                'What sections of law apply to this case?',
                'What steps should I take next?',
                'What documents should I gather?',
              ].map((sample, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.sampleItem}
                  onPress={() => setQuery(sample)}
                >
                  <Ionicons name="help-circle-outline" size={16} color="#2196F3" />
                  <Text style={styles.sampleText}>{sample}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </>
        ) : (
          <>
            {/* Category & Summary */}
            <View style={styles.resultHeader}>
              <View style={styles.categoryBadge}>
                <Text style={styles.categoryText}>{result.category.replace('_', ' ').toUpperCase()}</Text>
              </View>
              <Text style={styles.summaryText}>{result.query_summary}</Text>
            </View>

            {/* Main Advice */}
            <View style={styles.adviceCard}>
              <View style={styles.adviceHeader}>
                <Ionicons name="book" size={20} color="#2196F3" />
                <Text style={styles.adviceTitle}>Legal Guidance</Text>
              </View>
              <Text style={styles.adviceText}>{result.advice}</Text>
            </View>

            {/* Relevant Provisions */}
            {result.relevant_provisions?.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Relevant Provisions</Text>
                {result.relevant_provisions.map((provision, index) => (
                  <View key={index} style={styles.provisionCard}>
                    <Text style={styles.provisionAct}>{provision.act}</Text>
                    <Text style={styles.provisionSection}>{provision.section}</Text>
                    <Text style={styles.provisionDesc} numberOfLines={3}>
                      {provision.description}
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {/* Case References */}
            {result.case_references?.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Case References</Text>
                {result.case_references.map((caseRef, index) => (
                  <View key={index} style={styles.caseCard}>
                    <Text style={styles.caseName}>{caseRef.case_name}</Text>
                    <Text style={styles.caseMeta}>
                      {caseRef.year && `${caseRef.year}`}
                      {caseRef.court && ` • ${caseRef.court}`}
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {/* Disclaimers */}
            <View style={styles.disclaimerCard}>
              <Ionicons name="warning" size={20} color="#FF9800" />
              <View style={styles.disclaimerContent}>
                <Text style={styles.disclaimerTitle}>Important Disclaimers</Text>
                {result.disclaimers.map((disclaimer, index) => (
                  <Text key={index} style={styles.disclaimerText}>• {disclaimer}</Text>
                ))}
              </View>
            </View>

            {/* Download Buttons */}
            <View style={styles.downloadSection}>
              <Text style={styles.downloadTitle}>Download Legal Advice</Text>
              <View style={styles.downloadButtons}>
                <TouchableOpacity
                  style={[styles.downloadButton, styles.pdfButton, downloading === 'pdf' && styles.downloadButtonDisabled]}
                  onPress={() => handleDownload('pdf')}
                  disabled={downloading !== null}
                >
                  {downloading === 'pdf' ? (
                    <ActivityIndicator size="small" color="#fff" />
                  ) : (
                    <>
                      <Ionicons name="document-text" size={20} color="#fff" />
                      <Text style={styles.downloadButtonText}>PDF</Text>
                    </>
                  )}
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.downloadButton, styles.docButton, downloading === 'doc' && styles.downloadButtonDisabled]}
                  onPress={() => handleDownload('doc')}
                  disabled={downloading !== null}
                >
                  {downloading === 'doc' ? (
                    <ActivityIndicator size="small" color="#fff" />
                  ) : (
                    <>
                      <Ionicons name="file-tray-stacked" size={20} color="#fff" />
                      <Text style={styles.downloadButtonText}>DOC</Text>
                    </>
                  )}
                </TouchableOpacity>
              </View>
            </View>

            <TouchableOpacity style={styles.anotherButton} onPress={handleClear}>
              <Text style={styles.anotherButtonText}>Ask Another Question</Text>
            </TouchableOpacity>
          </>
        )}
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
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  content: {
    flex: 1,
  },
  contentPadding: {
    padding: 20,
    paddingBottom: 40,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    minHeight: 120,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: '#eee',
    marginBottom: 16,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFEBEE',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    gap: 8,
  },
  errorText: {
    flex: 1,
    color: '#FF5252',
    fontSize: 14,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  secondaryButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonDisabled: {
    backgroundColor: '#A5D6A7',
  },
  samplesContainer: {
    backgroundColor: '#f9f9f9',
    padding: 16,
    borderRadius: 12,
  },
  samplesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 12,
  },
  sampleItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    gap: 8,
  },
  sampleText: {
    fontSize: 14,
    color: '#2196F3',
    flex: 1,
  },
  // Result styles
  resultHeader: {
    marginBottom: 20,
  },
  categoryBadge: {
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: 'flex-start',
    marginBottom: 8,
  },
  categoryText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  summaryText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  adviceCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#eee',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  adviceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  adviceTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  adviceText: {
    fontSize: 15,
    color: '#333',
    lineHeight: 26,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 12,
  },
  provisionCard: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  provisionAct: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  provisionSection: {
    fontSize: 12,
    color: '#2196F3',
    marginBottom: 4,
  },
  provisionDesc: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
  caseCard: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  caseName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  caseMeta: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  disclaimerCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF3E0',
    padding: 16,
    borderRadius: 12,
    gap: 12,
    marginBottom: 20,
  },
  disclaimerContent: {
    flex: 1,
  },
  disclaimerTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#E65100',
    marginBottom: 8,
  },
  disclaimerText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
  anotherButton: {
    backgroundColor: '#2196F3',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  anotherButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  downloadSection: {
    backgroundColor: '#f9f9f9',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  downloadTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 12,
    textAlign: 'center',
  },
  downloadButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  downloadButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 14,
    borderRadius: 10,
    gap: 8,
  },
  pdfButton: {
    backgroundColor: '#F44336',
  },
  docButton: {
    backgroundColor: '#2196F3',
  },
  downloadButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  downloadButtonDisabled: {
    opacity: 0.6,
  },
});
