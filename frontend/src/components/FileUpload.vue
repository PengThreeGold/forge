<template>
  <div class="file-upload-container">
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :headers="headers"
      :multiple="multiple"
      :data="data"
      :name="name"
      :with-credentials="withCredentials"
      :show-file-list="showFileList"
      :drag="drag"
      :accept="accept"
      :list-type="listType"
      :auto-upload="autoUpload"
      :disabled="disabled"
      :limit="limit"
      :on-exceed="handleExceed"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :on-preview="handlePreview"
      :before-upload="beforeUpload"
      :before-remove="beforeRemove"
      :http-request="httpRequest"
      :file-list="fileList"
    >
      <template #trigger>
        <slot name="trigger">
          <el-button type="primary" :disabled="disabled">
            <el-icon><Upload /></el-icon>
            {{ buttonText }}
          </el-button>
        </slot>
      </template>

      <template #default>
        <slot>
          <!-- 拖拽上传区域 -->
          <div v-if="drag" class="upload-drag-area">
            <el-icon class="upload-icon"><upload-filled /></el-icon>
            <div class="upload-text">
              <div>将文件拖拽到此处，或</div>
              <el-button type="primary" link>点击上传</el-button>
            </div>
          </div>

          <!-- 普通上传区域 -->
          <div v-else class="upload-normal-area">
            <el-button type="primary" :disabled="disabled">
              <el-icon><Upload /></el-icon>
              {{ buttonText }}
            </el-button>
          </div>
        </slot>
      </template>

      <template #tip>
        <slot name="tip">
          <div class="upload-tip" v-if="tip">
            {{ tip }}
          </div>
        </slot>
      </template>

      <template #file-list="{ files }">
        <slot name="file-list" :files="files">
          <ul class="el-upload-list">
            <li
              v-for="file in files"
              :key="file.uid"
              class="el-upload-list__item"
              :class="{
                'is-success': file.status === 'success',
                'is-uploading': file.status === 'uploading',
                'is-error': file.status === 'error',
              }"
            >
              <div class="el-upload-list__item-info">
                <span class="el-upload-list__item-name">
                  <el-icon><document /></el-icon>
                  <span class="el-upload-list__item-file-name" :title="file.name">
                    {{ file.name }}
                  </span>
                </span>
              </div>

              <div class="el-upload-list__item-actions">
                <!-- 预览按钮 -->
                <el-button
                  v-if="file.status === 'success' && showPreviewButton"
                  type="text"
                  @click="handlePreview(file)"
                >
                  <el-icon><zoom-in /></el-icon>
                </el-button>

                <!-- 下载按钮 -->
                <el-button
                  v-if="file.status === 'success' && showDownloadButton"
                  type="text"
                  @click="handleDownload(file)"
                >
                  <el-icon><download /></el-icon>
                </el-button>

                <!-- 删除按钮 -->
                <el-button v-if="showRemoveButton" type="text" @click="handleRemove(file)">
                  <el-icon><delete /></el-icon>
                </el-button>
              </div>

              <!-- 上传进度 -->
              <el-progress
                v-if="file.status === 'uploading'"
                :percentage="file.percentage || 0"
                :stroke-width="2"
                :show-text="false"
              />
            </li>
          </ul>
        </slot>
      </template>
    </el-upload>

    <!-- 文件预览对话框 -->
    <el-dialog v-model="previewVisible" :title="previewTitle" width="50%" append-to-body>
      <div class="preview-container">
        <slot name="preview" :file="previewFile">
          <!-- 图片预览 -->
          <div v-if="isImage(previewFile)" class="image-preview">
            <img :src="previewFile.url" :alt="previewFile.name" />
          </div>

          <!-- 文本预览 -->
          <div v-else-if="isText(previewFile)" class="text-preview">
            <pre>{{ previewText }}</pre>
          </div>

          <!-- 其他类型文件 -->
          <div v-else class="default-preview">
            <el-empty description="无法预览此类型文件" />
          </div>
        </slot>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, computed, watch } from 'vue'
import { ElUpload, ElButton, ElIcon, ElProgress, ElDialog, ElEmpty, ElMessage } from 'element-plus'
import { Upload, UploadFilled, Document, ZoomIn, Download, Delete } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'FileUpload',
  components: {
    ElUpload,
    ElButton,
    ElIcon,
    ElProgress,
    ElDialog,
    ElEmpty,
    Upload,
    UploadFilled,
    Document,
    ZoomIn,
    Download,
    Delete,
  },
  props: {
    // 基础属性
    uploadUrl: {
      type: String,
      required: true,
    },
    headers: {
      type: Object,
      default: () => ({}),
    },
    multiple: {
      type: Boolean,
      default: false,
    },
    data: {
      type: Object,
      default: () => ({}),
    },
    name: {
      type: String,
      default: 'file',
    },
    withCredentials: {
      type: Boolean,
      default: false,
    },
    showFileList: {
      type: Boolean,
      default: true,
    },
    drag: {
      type: Boolean,
      default: false,
    },
    accept: {
      type: String,
      default: '',
    },
    listType: {
      type: String,
      default: 'text',
    },
    autoUpload: {
      type: Boolean,
      default: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    limit: {
      type: Number,
      default: 5,
    },

    // 自定义属性
    buttonText: {
      type: String,
      default: '上传文件',
    },
    tip: {
      type: String,
      default: '',
    },
    showPreviewButton: {
      type: Boolean,
      default: true,
    },
    showDownloadButton: {
      type: Boolean,
      default: true,
    },
    showRemoveButton: {
      type: Boolean,
      default: true,
    },
    fileSizeLimit: {
      type: Number,
      default: 0, // 0表示不限制，单位为MB
    },
    allowedFileTypes: {
      type: Array,
      default: () => [], // 允许的文件类型，如 ['.jpg', '.png', '.gif']
    },
  },
  emits: [
    'exceed',
    'success',
    'error',
    'change',
    'remove',
    'preview',
    'before-upload',
    'before-remove',
    'download',
  ],
  setup(props, { emit }) {
    const uploadRef = ref(null)
    const fileList = ref([])
    const previewVisible = ref(false)
    const previewFile = ref(null)
    const previewText = ref('')

    // 计算属性
    const previewTitle = computed(() => {
      return previewFile.value ? `预览: ${previewFile.value.name}` : '文件预览'
    })

    // 监听文件列表变化
    watch(
      fileList,
      newVal => {
        emit('change', newVal)
      },
      { deep: true }
    )

    // 处理文件超出限制
    const handleExceed = (files, fileList) => {
      ElMessage.warning(`最多只能上传 ${props.limit} 个文件`)
      emit('exceed', files, fileList)
    }

    // 处理上传成功
    const handleSuccess = (response, uploadFile, uploadFiles) => {
      ElMessage.success('上传成功')
      emit('success', response, uploadFile, uploadFiles)
    }

    // 处理上传失败
    const handleError = (error, uploadFile, uploadFiles) => {
      ElMessage.error('上传失败')
      emit('error', error, uploadFile, uploadFiles)
    }

    // 处理文件变化
    const handleChange = (uploadFile, uploadFiles) => {
      fileList.value = uploadFiles
      emit('change', uploadFile, uploadFiles)
    }

    // 处理文件移除
    const handleRemove = (file, fileList) => {
      ElMessage.info('文件已移除')
      emit('remove', file, fileList)
    }

    // 处理文件预览
    const handlePreview = async file => {
      previewFile.value = file

      // 如果是文本文件，读取内容
      if (isText(file)) {
        try {
          const response = await fetch(file.url)
          previewText.value = await response.text()
        } catch (error) {
          console.error('读取文件内容失败:', error)
          previewText.value = '读取文件内容失败'
        }
      }

      previewVisible.value = true
      emit('preview', file)
    }

    // 处理文件下载
    const handleDownload = file => {
      const link = document.createElement('a')
      link.href = file.url
      link.download = file.name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      emit('download', file)
    }

    // 上传前钩子
    const beforeUpload = file => {
      // 检查文件大小
      if (props.fileSizeLimit > 0 && file.size > props.fileSizeLimit * 1024 * 1024) {
        ElMessage.error(`文件大小不能超过 ${props.fileSizeLimit}MB`)
        return false
      }

      // 检查文件类型
      if (props.allowedFileTypes.length > 0) {
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
        if (!props.allowedFileTypes.includes(fileExtension)) {
          ElMessage.error(`只允许上传 ${props.allowedFileTypes.join(', ')} 类型的文件`)
          return false
        }
      }

      const result = emit('before-upload', file)
      if (result === false) {
        return false
      }
      return true
    }

    // 移除前钩子
    const beforeRemove = (file, fileList) => {
      const result = emit('before-remove', file, fileList)
      if (result === false) {
        return false
      }
      return true
    }

    // 自定义上传方法
    const httpRequest = options => {
      emit('http-request', options)
    }

    // 判断是否为图片
    const isImage = file => {
      if (!file || !file.name) return false
      const imageTypes = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
      const extension = '.' + file.name.split('.').pop().toLowerCase()
      return imageTypes.includes(extension)
    }

    // 判断是否为文本文件
    const isText = file => {
      if (!file || !file.name) return false
      const textTypes = ['.txt', '.json', '.xml', '.html', '.css', '.js', '.vue', '.md']
      const extension = '.' + file.name.split('.').pop().toLowerCase()
      return textTypes.includes(extension)
    }

    // 暴露方法
    const submit = () => {
      uploadRef.value?.submit()
    }

    const clearFiles = () => {
      uploadRef.value?.clearFiles()
    }

    const abort = file => {
      uploadRef.value?.abort(file)
    }

    return {
      uploadRef,
      fileList,
      previewVisible,
      previewFile,
      previewText,
      previewTitle,
      handleExceed,
      handleSuccess,
      handleError,
      handleChange,
      handleRemove,
      handlePreview,
      handleDownload,
      beforeUpload,
      beforeRemove,
      httpRequest,
      isImage,
      isText,
      submit,
      clearFiles,
      abort,
    }
  },
})
</script>

<style scoped>
.file-upload-container {
  width: 100%;
}

.upload-drag-area {
  width: 360px;
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-drag-area:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  text-align: center;
  color: #606266;
  line-height: 1.5;
}

.upload-normal-area {
  display: flex;
  align-items: center;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

.el-upload-list {
  margin-top: 10px;
}

.el-upload-list__item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.el-upload-list__item:hover {
  background-color: #f5f7fa;
}

.el-upload-list__item-info {
  flex: 1;
  overflow: hidden;
}

.el-upload-list__item-name {
  display: flex;
  align-items: center;
  color: #606266;
}

.el-upload-list__item-file-name {
  margin-left: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.el-upload-list__item-actions {
  display: flex;
  margin-left: 12px;
}

.preview-container {
  max-height: 60vh;
  overflow: auto;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

.text-preview {
  max-height: 60vh;
  overflow: auto;
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
}

.text-preview pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.default-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

/* 暗色主题 */
.dark-theme .upload-drag-area {
  background-color: #1d2935;
  border-color: #4c4d4f;
}

.dark-theme .upload-drag-area:hover {
  border-color: #79bbff;
}

.dark-theme .upload-icon {
  color: #7c7e81;
}

.dark-theme .upload-text {
  color: #a8abb2;
}

.dark-theme .el-upload-list__item:hover {
  background-color: #2c3e50;
}

.dark-theme .el-upload-list__item-name {
  color: #a8abb2;
}

.dark-theme .text-preview {
  background-color: #2c3e50;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-drag-area {
    width: 100%;
    height: 150px;
  }
}
</style>
