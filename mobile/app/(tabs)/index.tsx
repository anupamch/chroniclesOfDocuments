import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, View, Text, FlatList, TouchableOpacity, RefreshControl, ActivityIndicator, Alert, BackHandler, ToastAndroid, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { getCases, deleteCase, Case, PaginatedCases } from '../../lib/api';

export default function CaseListScreen() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const router = useRouter();

  const fetchCases = useCallback(async (pageNum = 1, isRefreshing = false) => {
    try {
      if (pageNum === 1) setLoading(!isRefreshing);
      else setLoadingMore(true);

      const data = await getCases(pageNum);
      if (pageNum === 1) {
        setCases(data.cases);
      } else {
        setCases(prev => [...prev, ...data.cases]);
      }
      setHasMore(pageNum < data.total_pages);
      setPage(pageNum);
    } catch (error) {
      console.error('Fetch cases error:', error);
      Alert.alert('Error', 'Failed to fetch cases');
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  }, []);

  const handleDeleteCase = (id: string) => {
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
              await deleteCase(id);
              fetchCases(1, true); // Refresh
            } catch (error: any) {
              Alert.alert('Error', error.message);
            }
          }
        }
      ]
    );
  };

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  useEffect(() => {
    let backPressCount = 0;
    let backPressTimer: any = null;

    const backAction = () => {
      // Only handle if we are on the case list screen
      if (Platform.OS === 'android') {
        if (backPressCount === 1) {
          BackHandler.exitApp();
          return true;
        }

        backPressCount++;
        ToastAndroid.show('Press back again to exit', ToastAndroid.SHORT);
        
        if (backPressTimer) clearTimeout(backPressTimer);
        backPressTimer = setTimeout(() => {
          backPressCount = 0;
        }, 2000);

        return true;
      }
      return false;
    };

    const backHandler = BackHandler.addEventListener(
      'hardwareBackPress',
      backAction
    );

    return () => {
      backHandler.remove();
      if (backPressTimer) clearTimeout(backPressTimer);
    };
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchCases(1, true);
  };

  const onLoadMore = () => {
    if (!loadingMore && hasMore) {
      fetchCases(page + 1);
    }
  };

  const renderItem = ({ item }: { item: Case }) => (
    <TouchableOpacity 
      style={styles.caseCard} 
      onPress={() => router.push(`/cases/${item.case_id}`)}
    >
      <View style={styles.caseHeader}>
        <Text style={styles.caseNumber} numberOfLines={1}>{item.case_number}</Text>
      </View>
      <Text style={styles.caseTitle} numberOfLines={1}>{item.title}</Text>
      <View style={styles.caseFooter}>
        <View style={styles.docCount}>
          <Ionicons name="document-text-outline" size={16} color="#666" />
          <Text style={styles.footerText}>{item.total_documents || 0} docs</Text>
        </View>
        <Text style={styles.footerText}>{new Date(item.created_at).toLocaleDateString()}</Text>
      </View>
    </TouchableOpacity>
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={cases}
        renderItem={renderItem}
        keyExtractor={(item) => item.case_id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} color="#2196F3" />
        }
        onEndReached={onLoadMore}
        onEndReachedThreshold={0.5}
        ListFooterComponent={
          loadingMore ? (
            <ActivityIndicator style={{ marginVertical: 16 }} color="#2196F3" />
          ) : null
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="folder-open-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No cases found</Text>
          </View>
        }
      />
      <TouchableOpacity 
        style={styles.fab} 
        onPress={() => router.push('/cases/new')}
      >
        <Ionicons name="add" size={30} color="#fff" />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  listContent: {
    padding: 16,
  },
  caseCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  caseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  caseNumber: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2196F3',
    fontFamily: 'System',
    flex: 1,
    marginRight: 10,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  caseTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 12,
  },
  caseFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12,
  },
  docCount: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  footerText: {
    fontSize: 12,
    color: '#666',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    marginTop: 100,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
    color: '#999',
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    backgroundColor: '#2196F3',
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  deleteIcon: {
    padding: 4,
  },
});
