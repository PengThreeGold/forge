<template>
  <div class="enhanced-file-upload">
    <el-upload
      ref="upload"
      class="upload-demo"
      drag
      :action="action"
      :headers="headers"
      :data="data"
      :auto-upload="autoUpload"
      :show-file-list="showFileList"
      :limit="limit"
      :accept="accept"
      :multiple="multiple"
      :file-list="fileList"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-progress="handleProgress"
      :before-upload="beforeUpload"
      :on-exceed="handleExceed"
      :disabled="disabled || uploading"
    >
      <div class="upload-content">
        <el-icon class="upload-icon" :size="48" v-if="!uploading">
          <UploadFilled />
        </el-icon>
        <el-progress
          v-else
          type="circle"
          :percentage="uploadProgress"
          :width="48"
          :status="uploadStatus"
        />
        <div class="upload-text">
          <p v-if="!uploading">将文件拖到此处，或<em>点击上传</em></p>
          <p v-else>正在上传... {{ uploadProgress }}%</p>
        </div>
      </div>
    </el-upload>

    <!-- 上传信息 -->
    <div v-if="showInfo && selectedFile" class="upload-info">
      <div class="info-item">
        <span class="info-label">文件名:</span>
        <span class="info-value">{{ selectedFile.name }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">文件大小:</span>
        <span class="info-value">{{ formatFileSize(selectedFile.size) }}</span>
      </div>
      <div class="info-item" v-if="selectedFile.type">
        <span class="info-label">文件类型:</span>
        <span class="info-value">{{ selectedFile.type }}</span>
      </div>
    </div>

    <!-- 上传提示 -->
    <div class="upload-tips" v-if="tips">
      <el-alert :title="tips.title" type="info" :closable="false" show-icon>
        <div v-if="tips.content" v-html="tips.content"></div>
      </el-alert>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'EnhancedFileUpload',
  components: {
    UploadFilled,
  },
  props: {
    // 上传地址
    action: {
      type: String,
      required: true,
    },
    // 上传时附带的额外参数
    data: {
      type: Object,
      default: () => ({}),
    },
    // 设置上传的请求头部
    headers: {
      type: Object,
      default: () => ({}),
    },
    // 是否自动上传
    autoUpload: {
      type: Boolean,
      default: true,
    },
    // 是否显示已上传文件列表
    showFileList: {
      type: Boolean,
      default: false,
    },
    // 最大上传数量
    limit: {
      type: Number,
      default: 1,
    },
    // 接受的文件类型
    accept: {
      type: String,
      default: '',
    },
    // 是否支持多选
    multiple: {
      type: Boolean,
      default: false,
    },
    // 文件列表
    modelValue: {
      type: Array,
      default: () => [],
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      default: false,
    },
    // 最大文件大小（字节）
    maxSize: {
      type: Number,
      default: 500 * 1024 * 1024, // 500MB
    },
    // 是否显示上传信息
    showInfo: {
      type: Boolean,
      default: true,
    },
    // 上传提示信息
    tips: {
      type: Object,
      default: () => null,
    },
  },
  emits: ['update:modelValue', 'change', 'success', 'error', 'progress', 'remove'],
  setup(props, { emit }) {
    const upload = ref(null)
    const fileList = ref([])
    const selectedFile = ref(null)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')

    // 监听外部文件列表变化
    watch(
      () => props.modelValue,
      newVal => {
        fileList.value = [...newVal]
      },
      { immediate: true, deep: true }
    )

    // 文件选择变化
    const handleChange = (file, files) => {
      selectedFile.value = file.raw || file

      // 更新文件列表
      fileList.value = [...files]

      // 发出更新事件
      emit('update:modelValue', files)
      emit('change', file, files)
    }

    // 文件移除
    const handleRemove = (file, files) => {
      selectedFile.value =
        files.length > 0 ? files[files.length - 1].raw || files[files.length - 1] : null

      // 更新文件列表
      fileList.value = [...files]

      // 发出更新事件
      emit('update:modelValue', files)
      emit('remove', file, files)
    }

    // 上传成功
    const handleSuccess = (response, file, files) => {
      uploading.value = false
      uploadProgress.value = 100
      uploadStatus.value = 'success'

      ElMessage.success('上传成功')
      emit('success', response, file, files)

      // 重置上传状态
      setTimeout(() => {
        uploading.value = false
        uploadProgress.value = 0
        uploadStatus.value = ''
      }, 1000)
    }

    // 上传错误
    const handleError = (error, file, files) => {
      uploading.value = false
      uploadProgress.value = 0
      uploadStatus.value = 'exception'

      ElMessage.error('上传失败: ' + (error.message || '未知错误'))
      emit('error', error, file, files)
    }

    // 上传进度
    const handleProgress = (event, file, files) => {
      uploadProgress.value = Math.round(event.percent)
      emit('progress', event, file, files)
    }

    // 上传前检查
    const beforeUpload = file => {
      // 检查文件大小
      if (file.size > props.maxSize) {
        ElMessage.error(`文件大小不能超过 ${formatFileSize(props.maxSize)}`)
        return false
      }

      // 如果不是自动上传，设置上传状态
      if (!props.autoUpload) {
        uploading.value = true
        uploadStatus.value = ''
      }

      return true
    }

    // 超出上传限制
    const handleExceed = (files, fileList) => {
      ElMessage.warning(`最多只能上传 ${props.limit} 个文件`)
    }

    // 手动上传
    const submit = () => {
      if (upload.value) {
        uploading.value = true
        upload.value.submit()
      }
    }

    // 清空文件列表
    const clearFiles = () => {
      if (upload.value) {
        upload.value.clearFiles()
      }
      fileList.value = []
      selectedFile.value = null
      emit('update:modelValue', [])
    }

    // 格式化文件大小
    const formatFileSize = size => {
      if (size === 0) return '0 B'

      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(size) / Math.log(k))

      return parseFloat((size / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    return {
      upload,
      fileList,
      selectedFile,
      uploading,
      uploadProgress,
      uploadStatus,
      handleChange,
      handleRemove,
      handleSuccess,
      handleError,
      handleProgress,
      beforeUpload,
      handleExceed,
      submit,
      clearFiles,
      formatFileSize,
      UploadFilled,
    }
  },
})
</script>

<style scoped>
.enhanced-file-upload {
  width: 100%;
}

.upload-demo {
  width: 100%;
}

.upload-content {
  padding: 20px;
  text-align: center;
  cursor: pointer;
}

.upload-icon {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.upload-text p em {
  color: #409eff;
  font-style: normal;
}

.upload-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #909399;
  font-size: 14px;
}

.info-value {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.upload-tips {
  margin-top: 12px;
}

/* 暗色主题 */
.dark-theme .upload-icon {
  color: #4c4d4f;
}

.dark-theme .upload-text p {
  color: #cfd3dc;
}

.dark-theme .upload-info {
  background-color: #1d2935;
}

.dark-theme .info-label {
  color: #7c7e81;
}

.dark-theme .info-value {
  color: #e5eaf3;
}

/* 拖拽区域样式 */
:deep(.el-upload-dragger) {
  background-color: #fafafa;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  box-sizing: border-box;
  width: 100%;
  height: 180px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.05);
}

:deep(.el-upload-dragger.is-dragover) {
  background-color: rgba(32, 159, 255, 0.1);
  border: 2px dashed #409eff;
}

.dark-theme :deep(.el-upload-dragger) {
  background-color: #141414;
  border-color: #4c4d4f;
}

.dark-theme :deep(.el-upload-dragger:hover) {
  border-color: #79bbff;
  background-color: rgba(121, 187, 255, 0.05);
}

.dark-theme :deep(.el-upload-dragger.is-dragover) {
  background-color: rgba(121, 187, 255, 0.1);
  border-color: #79bbff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-upload-dragger) {
    height: 140px;
  }

  .upload-content {
    padding: 15px;
  }

  .upload-icon {
    font-size: 40px;
    margin-bottom: 12px;
  }
}
</style>
