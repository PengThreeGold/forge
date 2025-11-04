<template>
  <div class="software-release-container" v-loading="loading">
    <div class="page-header">
      <div class="header-title">
        <el-button icon="ArrowLeft" circle @click="goBack" />
        <h2>{{ space.name }} - 版本发布</h2>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateReleaseDialog">
          <el-icon><Plus /></el-icon>
          发布新版本
        </el-button>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="release-list">
        <div v-if="versions.length === 0" class="empty-state">
          <el-empty description="暂无版本">
            <el-button type="primary" @click="showCreateReleaseDialog">创建第一个版本</el-button>
          </el-empty>
        </div>

        <div v-for="(version, index) in versions" :key="version.id" class="release-item">
          <el-card shadow="hover" class="release-card">
            <div class="release-header">
              <div class="release-info">
                <div class="release-tag">
                  <el-tag :type="version.is_latest ? 'danger' : 'primary'" size="large">
                    {{ version.version }}
                  </el-tag>
                  <el-tag v-if="version.is_latest" type="danger" size="small">Latest</el-tag>
                  <el-tag v-if="version.is_prerelease" type="warning" size="small"
                    >Pre-release</el-tag
                  >
                </div>
                <div class="release-meta">
                  <span class="release-date">
                    {{ formatDateTime(version.publish_date || version.created_at) }}
                  </span>
                  <span class="release-author">发布者: {{ version.author || 'Unknown' }}</span>
                </div>
              </div>
              <div class="release-actions">
                <el-dropdown trigger="click" @command="cmd => handleAction(cmd, version)">
                  <el-button type="text" :icon="MoreFilled" />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit" :disabled="!version.is_published">
                        <el-icon><Edit /></el-icon>
                        编辑发布说明
                      </el-dropdown-item>
                      <el-dropdown-item command="download" :disabled="!version.is_published">
                        <el-icon><Download /></el-icon>
                        下载
                      </el-dropdown-item>
                      <el-dropdown-item command="publish" v-if="!version.is_published">
                        <el-icon><Check /></el-icon>
                        发布版本
                      </el-dropdown-item>
                      <el-dropdown-item command="unpublish" v-if="version.is_published">
                        <el-icon><Close /></el-icon>
                        取消发布
                      </el-dropdown-item>
                      <el-dropdown-item command="setLatest" v-if="!version.is_latest">
                        <el-icon><Star /></el-icon>
                        设为最新版
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        <el-icon><Delete /></el-icon>
                        删除版本
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>

            <div class="release-content">
              <div class="release-description" v-if="version.release_note">
                <div
                  class="description-content"
                  v-html="formatReleaseNote(version.release_note)"
                ></div>
                <el-button
                  v-if="version.release_note.length > 300"
                  type="text"
                  @click="toggleDescription(index)"
                >
                  {{ version.showFull ? '收起' : '展开全部' }}
                </el-button>
              </div>
              <div class="release-description" v-else>
                <p class="no-description">暂无发布说明</p>
              </div>

              <div class="release-assets" v-if="version.is_published">
                <div class="assets-header">
                  <h4>资源下载</h4>
                  <el-button type="text" size="small" @click="toggleAssets(index)">
                    {{ version.showAssets ? '收起' : '展开' }}
                  </el-button>
                </div>
                <div v-show="version.showAssets" class="assets-list">
                  <div class="asset-item">
                    <div class="asset-info">
                      <el-icon class="asset-icon"><Document /></el-icon>
                      <span class="asset-name">{{ version.version }} 安装包</span>
                      <span class="asset-size">{{ version.file_size_human || '未知大小' }}</span>
                    </div>
                    <el-button
                      type="primary"
                      size="small"
                      @click="downloadVersion(version)"
                      :loading="downloading === version.id"
                    >
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                  </div>
                </div>
              </div>

              <div class="release-stats">
                <div class="stat-item">
                  <el-icon><Download /></el-icon>
                  <span>{{ version.download_count || 0 }} 次下载</span>
                </div>
                <div class="stat-item">
                  <el-icon><User /></el-icon>
                  <span>{{ version.unique_downloaders || 0 }} 位独立用户</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 创建/编辑发布对话框 -->
    <el-dialog
      v-model="releaseDialogVisible"
      :title="isEditing ? '编辑发布' : '创建新发布'"
      width="800px"
      :close-on-click-modal="false"
      class="release-dialog"
    >
      <el-form ref="releaseFormRef" :model="releaseForm" :rules="releaseRules" label-width="120px">
        <el-form-item label="版本号" prop="version">
          <el-input
            v-model="releaseForm.version"
            placeholder="例如: 1.0.0, 2.1.0-beta"
            :disabled="isEditing"
          />
        </el-form-item>

        <el-form-item label="发布标题" prop="title">
          <el-input v-model="releaseForm.title" placeholder="输入发布的标题" />
        </el-form-item>

        <el-form-item label="发布说明" prop="release_note">
          <el-input
            v-model="releaseForm.release_note"
            type="textarea"
            :rows="8"
            placeholder="详细描述此版本的更新内容和改进..."
          />
        </el-form-item>

        <el-form-item label="上传文件" prop="file" v-if="!isEditing">
          <el-upload
            ref="upload"
            class="release-upload"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :file-list="fileList"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .exe, .msi, .dmg, .pkg, .deb, .rpm, .zip, .tar.gz 等格式，且不超过 500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="releaseForm.is_prerelease"> 这是一个预发布版本 </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="releaseForm.set_as_latest"> 设为最新版本 </el-checkbox>
        </el-form-item>

        <el-form-item label="发布类型" prop="release_type">
          <el-radio-group v-model="releaseForm.release_type">
            <el-radio label="major">主要版本 (Major)</el-radio>
            <el-radio label="minor">次要版本 (Minor)</el-radio>
            <el-radio label="patch">补丁版本 (Patch)</el-radio>
            <el-radio label="prerelease">预发布 (Pre-release)</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="releaseDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="releaseLoading" @click="handleReleaseSubmit">
            {{ isEditing ? '保存' : '发布' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  ArrowLeft,
  MoreFilled,
  Edit,
  Download,
  Check,
  Close,
  Star,
  Delete,
  Document,
  UploadFilled,
  User,
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/common'

export default defineComponent({
  name: 'SoftwareRelease',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()

    // 数据
    const space = ref({})
    const versions = ref([])
    const loading = ref(false)
    const downloading = ref(null)

    // 对话框相关
    const releaseDialogVisible = ref(false)
    const releaseLoading = ref(false)
    const isEditing = ref(false)
    const currentVersion = ref(null)

    // 表单
    const releaseForm = reactive({
      version: '',
      title: '',
      release_note: '',
      is_prerelease: false,
      set_as_latest: true,
      release_type: 'patch',
      file: null,
    })

    const releaseRules = {
      version: [
        { required: true, message: '请输入版本号', trigger: 'blur' },
        {
          pattern: /^(v?\d+\.\d+\.\d+(-[\w.]+)?)|(\d+\.\d+\.\d+(-[\w.]+)?)$/,
          message: '版本号格式不正确',
          trigger: 'blur',
        },
      ],
      title: [{ required: true, message: '请输入发布标题', trigger: 'blur' }],
      file: [{ required: true, message: '请选择文件', trigger: 'change' }],
    }

    const releaseFormRef = ref(null)
    const fileList = ref([])
    const upload = ref(null)

    // 计算属性
    const spaceId = computed(() => route.params.id)

    // 获取软件空间详情
    const getSpaceDetail = async () => {
      try {
        loading.value = true
        const response = await store.dispatch('software/getSpace', spaceId.value)
        space.value = response.data

        // 获取版本列表
        await getVersions(spaceId.value)
      } catch (error) {
        console.error('获取软件空间详情失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 获取版本列表
    const getVersions = async spaceId => {
      try {
        const response = await store.dispatch('software/getVersions', spaceId)
        versions.value = response.data.map(version => ({
          ...version,
          showFull: false,
          showAssets: false,
        }))
      } catch (error) {
        console.error('获取版本列表失败:', error)
      }
    }

    // 显示创建发布对话框
    const showCreateReleaseDialog = () => {
      isEditing.value = false
      currentVersion.value = null
      resetReleaseForm()
      releaseDialogVisible.value = true
    }

    // 重置发布表单
    const resetReleaseForm = () => {
      releaseForm.version = ''
      releaseForm.title = ''
      releaseForm.release_note = ''
      releaseForm.is_prerelease = false
      releaseForm.set_as_latest = true
      releaseForm.release_type = 'patch'
      releaseForm.file = null
      fileList.value = []

      if (releaseFormRef.value) {
        releaseFormRef.value.resetFields()
      }

      if (upload.value) {
        upload.value.clearFiles()
      }
    }

    // 处理文件变化
    const handleFileChange = file => {
      releaseForm.file = file.raw
      fileList.value = [file]
    }

    // 处理文件移除
    const handleFileRemove = () => {
      releaseForm.file = null
      fileList.value = []
    }

    // 处理发布表单提交
    const handleReleaseSubmit = async () => {
      if (!releaseFormRef.value) return

      try {
        await releaseFormRef.value.validate()

        releaseLoading.value = true

        const versionData = {
          version: releaseForm.version,
          title: releaseForm.title,
          release_note: releaseForm.release_note,
          is_prerelease: releaseForm.is_prerelease,
          set_as_latest: releaseForm.set_as_latest,
          release_type: releaseForm.release_type,
          file: releaseForm.file,
        }

        if (isEditing.value) {
          // 编辑版本
          await store.dispatch('software/updateVersion', {
            versionId: currentVersion.value.id,
            versionData,
          })
          ElMessage.success('发布信息更新成功')
        } else {
          // 创建版本
          await store.dispatch('software/createVersion', {
            spaceId: spaceId.value,
            versionData,
          })
          ElMessage.success('版本发布成功')
        }

        releaseDialogVisible.value = false
        resetReleaseForm()

        // 重新获取版本列表
        await getVersions(spaceId.value)
      } catch (error) {
        console.error('发布版本失败:', error)
      } finally {
        releaseLoading.value = false
      }
    }

    // 处理操作
    const handleAction = async (command, version) => {
      switch (command) {
        case 'edit':
          editVersion(version)
          break
        case 'download':
          downloadVersion(version)
          break
        case 'publish':
          await publishVersion(version, true)
          break
        case 'unpublish':
          await publishVersion(version, false)
          break
        case 'setLatest':
          await setAsLatest(version)
          break
        case 'delete':
          confirmDeleteVersion(version)
          break
      }
    }

    // 编辑版本
    const editVersion = version => {
      isEditing.value = true
      currentVersion.value = version

      // 填充表单
      releaseForm.version = version.version
      releaseForm.title = version.title || version.version
      releaseForm.release_note = version.release_note || ''
      releaseForm.is_prerelease = version.is_prerelease || false
      releaseForm.set_as_latest = version.is_latest || false
      releaseForm.release_type = version.release_type || 'patch'

      releaseDialogVisible.value = true
    }

    // 下载版本
    const downloadVersion = async version => {
      try {
        downloading.value = version.id
        const response = await store.dispatch('software/downloadVersion', version.id)

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url

        // 获取文件名
        const contentDisposition = response.headers['content-disposition']
        let filename = `${version.version}`

        if (contentDisposition) {
          const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
          const matches = filenameRegex.exec(contentDisposition)
          if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '')
          }
        }

        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()

        // 清理
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('下载失败:', error)
      } finally {
        downloading.value = null
      }
    }

    // 发布/取消发布版本
    const publishVersion = async (version, publish) => {
      try {
        await store.dispatch('software/publishVersion', {
          versionId: version.id,
          publish,
        })

        ElMessage.success(publish ? '版本已发布' : '版本已取消发布')

        // 重新获取版本列表
        await getVersions(spaceId.value)
      } catch (error) {
        console.error('操作失败:', error)
      }
    }

    // 设为最新版本
    const setAsLatest = async version => {
      try {
        await store.dispatch('software/setAsLatest', {
          versionId: version.id,
        })

        ElMessage.success('已设为最新版本')

        // 重新获取版本列表
        await getVersions(spaceId.value)
      } catch (error) {
        console.error('操作失败:', error)
      }
    }

    // 确认删除版本
    const confirmDeleteVersion = version => {
      ElMessageBox.confirm(
        `确定要删除版本"${version.version}"吗？此操作不可逆，所有相关数据将被删除。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(async () => {
          try {
            await store.dispatch('software/deleteVersion', version.id)
            ElMessage.success('删除成功')

            // 重新获取版本列表
            await getVersions(spaceId.value)
          } catch (error) {
            console.error('删除版本失败:', error)
          }
        })
        .catch(() => {
          // 用户取消删除
        })
    }

    // 切换描述展开/收起
    const toggleDescription = index => {
      versions.value[index].showFull = !versions.value[index].showFull
    }

    // 切换资源列表展开/收起
    const toggleAssets = index => {
      versions.value[index].showAssets = !versions.value[index].showAssets
    }

    // 格式化发布说明
    const formatReleaseNote = note => {
      if (!note) return ''

      // 简单的Markdown转HTML
      return note
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>')
    }

    // 返回上一页
    const goBack = () => {
      router.push(`/software/${spaceId.value}`)
    }

    onMounted(() => {
      getSpaceDetail()
    })

    return {
      space,
      versions,
      loading,
      downloading,
      releaseDialogVisible,
      releaseLoading,
      isEditing,
      currentVersion,
      releaseForm,
      releaseRules,
      releaseFormRef,
      fileList,
      upload,
      spaceId,
      showCreateReleaseDialog,
      resetReleaseForm,
      handleFileChange,
      handleFileRemove,
      handleReleaseSubmit,
      handleAction,
      editVersion,
      downloadVersion,
      publishVersion,
      setAsLatest,
      confirmDeleteVersion,
      toggleDescription,
      toggleAssets,
      formatReleaseNote,
      goBack,
      formatDateTime,
      Plus,
      ArrowLeft,
      MoreFilled,
      Edit,
      Download,
      Check,
      Close,
      Star,
      Delete,
      Document,
      UploadFilled,
      User,
    }
  },
})
</script>

<style scoped>
.software-release-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-state {
  margin-top: 40px;
}

.release-item {
  margin-bottom: 20px;
}

.release-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.release-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.release-info {
  flex: 1;
}

.release-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.release-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #909399;
  font-size: 14px;
}

.release-actions {
  margin-left: 16px;
}

.release-content {
  padding-top: 16px;
}

.release-description {
  margin-bottom: 16px;
}

.description-content {
  line-height: 1.6;
  color: #606266;
  max-height: 120px;
  overflow: hidden;
}

.no-description {
  color: #909399;
  font-style: italic;
}

.release-assets {
  margin-bottom: 16px;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.assets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.assets-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.assets-list {
  background-color: #f9f9f9;
  border-radius: 6px;
  padding: 12px;
}

.asset-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.asset-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.asset-icon {
  color: #409eff;
}

.asset-name {
  font-weight: 500;
  color: #303133;
}

.asset-size {
  color: #909399;
  font-size: 14px;
}

.release-stats {
  display: flex;
  gap: 24px;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}

.release-dialog {
  border-radius: 8px;
}

.release-upload {
  width: 100%;
}

/* 暗色主题 */
.dark-theme .release-card {
  border-color: #4c4d4f;
  background-color: #1d2935;
}

.dark-theme .release-header {
  border-bottom-color: #4c4d4f;
}

.dark-theme .release-content {
  color: #e5eaf3;
}

.dark-theme .description-content {
  color: #cfd3dc;
}

.dark-theme .release-assets {
  border-top-color: #4c4d4f;
}

.dark-theme .assets-header h4 {
  color: #e5eaf3;
}

.dark-theme .assets-list {
  background-color: #141414;
}

.dark-theme .asset-name {
  color: #e5eaf3;
}

.dark-theme .release-stats {
  border-top-color: #4c4d4f;
}

.dark-theme .stat-item {
  color: #cfd3dc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .software-release-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .release-header {
    flex-direction: column;
    gap: 12px;
  }

  .release-actions {
    margin-left: 0;
  }

  .release-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .release-stats {
    flex-direction: column;
    gap: 12px;
  }

  .asset-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
