import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/views/layout/MainLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/views/forum/HomePage.vue') },
      { path: 'feed', name: 'feed', component: () => import('@/views/forum/FeedPage.vue') },
      { path: 'hot', name: 'hot', component: () => import('@/views/forum/HotRankPage.vue') },
      { path: 'sections/:category', name: 'section', component: () => import('@/views/forum/SectionPage.vue') },
      { path: 'boards/:boardId', name: 'board', component: () => import('@/views/forum/BoardPage.vue') },
      { path: 'posts/:postId', name: 'post-detail', component: () => import('@/views/content/PostDetailPage.vue') },
      { path: 'posts/new', name: 'create-post', component: () => import('@/views/content/CreatePostPage.vue') },
      { path: 'search', name: 'search', component: () => import('@/views/forum/SearchPage.vue') },
      { path: 'profile/me', name: 'my-profile', component: () => import('@/views/profile/MyProfilePage.vue') },
      { path: 'profile/:userId', name: 'user-profile', component: () => import('@/views/profile/UserProfilePage.vue') },
      { path: 'profile/me/edit', name: 'edit-profile', component: () => import('@/views/profile/EditProfilePage.vue') },
      { path: 'suitability', name: 'suitability', component: () => import('@/views/profile/SuitabilityPage.vue') },
      { path: 'admin', name: 'admin-dashboard', component: () => import('@/views/admin/AdminDashboard.vue') },
      { path: 'admin/posts', name: 'admin-posts', component: () => import('@/views/admin/AdminPostsPage.vue') },
      { path: 'admin/users', name: 'admin-users', component: () => import('@/views/admin/AdminUsersPage.vue') },
    ],
  },
  {
    path: '/auth',
    component: () => import('@/views/layout/AuthLayout.vue'),
    children: [
      { path: 'login', name: 'login', component: () => import('@/views/auth/LoginPage.vue') },
      { path: 'register', name: 'register', component: () => import('@/views/auth/RegisterPage.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const authPages = ['login', 'register']
  if (!token && !authPages.includes(to.name)) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
