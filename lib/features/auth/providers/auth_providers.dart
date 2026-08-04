import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../../core/network/api_client.dart';
import '../models/user.dart';
import '../models/auth.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(baseUrl: 'http://172.20.10.9:8001/api');
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.read(apiClientProvider));
});

class AuthRepository {
  final ApiClient _apiClient;

  AuthRepository(this._apiClient);

  Future<AuthResponse> login(String email, String password) async {
    final response = await _apiClient.dio.post(
      '/auth/login',
      data: LoginRequest(email: email, password: password).toJson(),
    );
    return AuthResponse.fromJson(response.data);
  }

  Future<AuthResponse> register({
    required String name,
    required String email,
    required String password,
    String? phoneNumber,
    String? role,
  }) async {
    final response = await _apiClient.dio.post(
      '/auth/register',
      data: RegisterRequest(
        email: email,
        password: password,
        fullName: name,
        phoneNumber: phoneNumber,
        role: role,
      ).toJson(),
    );
    return AuthResponse.fromJson(response.data);
  }

  Future<User> getProfile() async {
    final response = await _apiClient.dio.get('/auth/me');
    return User.fromJson(response.data);
  }

  Future<User> updateProfile({String? fullName, String? phoneNumber}) async {
    final response = await _apiClient.dio.put(
      '/auth/me',
      data: ProfileUpdateRequest(fullName: fullName, phoneNumber: phoneNumber).toJson(),
    );
    return User.fromJson(response.data);
  }

  Future<void> logout() async {
    await _apiClient.dio.post('/auth/logout');
  }
}

class AuthState {
  final User? user;
  final String? token;
  final bool isLoading;
  final String? error;

  const AuthState({
    this.user,
    this.token,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    User? user,
    String? token,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      token: token ?? this.token,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }

  bool get isAuthenticated => user != null && token != null;
  bool get isTourist => user?.isTourist ?? false;
  bool get isHost => user?.isHost ?? false;
  bool get isAdmin => user?.isAdmin ?? false;
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repository;
  final FlutterSecureStorage _storage;

  AuthNotifier(this._repository, this._storage) : super(const AuthState()) {
    _loadStoredAuth();
  }

  Future<void> _loadStoredAuth() async {
    state = state.copyWith(isLoading: true);
    try {
      final token = await _storage.read(key: 'auth_token');
      final userData = await _storage.read(key: 'user_data');
      
      if (token != null && userData != null) {
        final user = User.fromJson(userData as Map<String, dynamic>);
        state = state.copyWith(user: user, token: token, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _repository.login(email, password);
      await _storage.write(key: 'auth_token', value: response.accessToken);
      await _storage.write(key: 'user_data', value: response.user.toJson());
      
      state = state.copyWith(
        user: response.user,
        token: response.accessToken,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }

  Future<void> register({
    required String name,
    required String email,
    required String password,
    String? phoneNumber,
    String? role,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _repository.register(
        name: name,
        email: email,
        password: password,
        phoneNumber: phoneNumber,
        role: role,
      );
      await _storage.write(key: 'auth_token', value: response.accessToken);
      await _storage.write(key: 'user_data', value: response.user.toJson());
      
      state = state.copyWith(
        user: response.user,
        token: response.accessToken,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }

  Future<void> loadProfile() async {
    try {
      final user = await _repository.getProfile();
      await _storage.write(key: 'user_data', value: user.toJson());
      state = state.copyWith(user: user);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  Future<void> updateProfile({String? fullName, String? phoneNumber}) async {
    state = state.copyWith(isLoading: true);
    try {
      final user = await _repository.updateProfile(
        fullName: fullName,
        phoneNumber: phoneNumber,
      );
      await _storage.write(key: 'user_data', value: user.toJson());
      state = state.copyWith(user: user, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      rethrow;
    }
  }

  Future<void> logout() async {
    await _repository.logout();
    await _storage.delete(key: 'auth_token');
    await _storage.delete(key: 'user_data');
    state = const AuthState();
  }
}

final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.read(authRepositoryProvider),
    const FlutterSecureStorage(),
  );
});

final authStateProvider = Provider<AuthState>((ref) {
  return ref.watch(authNotifierProvider);
});

final isAuthenticatedProvider = Provider<bool>((ref) {
  final authState = ref.watch(authStateProvider);
  return authState.isAuthenticated;
});

final currentUserRoleProvider = Provider<UserRole?>((ref) {
  final authState = ref.watch(authStateProvider);
  if (authState.user != null) {
    return authState.user!.role.toUserRole();
  }
  return null;
});

final isTouristProvider = Provider<bool>((ref) {
  final role = ref.watch(currentUserRoleProvider);
  return role == UserRole.tourist;
});

final isHostProvider = Provider<bool>((ref) {
  final role = ref.watch(currentUserRoleProvider);
  return role == UserRole.businessOwner;
});

final isAdminProvider = Provider<bool>((ref) {
  final role = ref.watch(currentUserRoleProvider);
  return role == UserRole.admin;
});