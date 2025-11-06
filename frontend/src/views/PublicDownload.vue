<template>
  <div class="public-download-container">
    <el-card class="download-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <img src="@/assets/logo.png" alt="Forge" class="logo" />
            <div class="title-info">
              <h2>{{ spaceInfo?.name || "软件下载" }}</h2>
              <p class="version">{{ version }}</p>
            </div>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="goToHome">
              <el-icon><HomeFilled /></el-icon>
              返回首页
            </el-button>
          </div>
        </div>
      </template>

      <!-- 版本信息 -->
      <div class="version-info" v-loading="loading">
        <div class="info-item">
          <span class="label">版本号:</span>
          <span class="value">{{ versionInfo?.version }}</span>
        </div>
        <div class="info-item">
          <span class="label">发布说明:</span>
          <div
            class="value"
            v-html="formatReleaseNote(versionInfo?.release_note)"
          ></div>
        </div>
        <div class="info-item">
          <span class="label">发布时间:</span>
          <span class="value">{{
            formatDateTime(versionInfo?.publish_date)
          }}</span>
        </div>
        <div class="info-item" v-if="versionInfo?.documentation_url">
          <span class="label">文档链接:</span>
          <el-link
            :href="versionInfo.documentation_url"
            target="_blank"
            type="primary"
          >
            查看文档
          </el-link>
        </div>
      </div>

      <!-- 文件下载列表 -->
      <div class="download-section">
        <h3>文件下载</h3>
        <el-table
          v-loading="filesLoading"
          :data="fileList"
          border
          style="width: 100%"
        >
          <el-table-column prop="architecture" label="架构" width="120" />
          <el-table-column
            prop="filename"
            label="文件名"
            min-width="200"
            show-overflow-tooltip
          />
          <el-table-column
            prop="file_size_human"
            label="文件大小"
            width="120"
          />
          <el-table-column
            prop="file_hash"
            label="文件哈希"
            min-width="200"
            show-overflow-tooltip
          />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" @click="handleDownload(row)">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 页脚 -->
    <div class="footer">
      <p>Powered by Forge 软件发布管理平台</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";

export default {
  name: "PublicDownload",
  setup() {
    const route = useRoute();
    const router = useRouter();

    // 响应式数据
    const loading = ref(false);
    const filesLoading = ref(false);
    const spaceInfo = ref(null);
    const versionInfo = ref(null);
    const fileList = ref([]);

    // 计算属性
    const spaceId = route.params.spaceId;
    const version = route.params.version;

    // 方法
    const fetchVersionInfo = async () => {
      if (!spaceId || !version) {
        ElMessage.error("参数错误");
        return;
      }

      loading.value = true;
      try {
        // 这里应该调用公开API获取版本信息
        // 暂时使用模拟数据
        versionInfo.value = {
          version: version,
          release_note:
            "这是一个示例版本，包含了一些新功能和修复。<ul><li>新功能1</li><li>新功能2</li><li>修复了一些bug</li></ul>",
          publish_date: new Date().toISOString(),
        };
      } catch (error) {
        ElMessage.error("获取版本信息失败");
      } finally {
        loading.value = false;
      }
    };

    const fetchFiles = async () => {
      filesLoading.value = true;
      try {
        // 这里应该调用公开API获取文件列表
        // 暂时使用模拟数据
        fileList.value = [
          {
            id: 1,
            architecture: "Windows x64",
            filename: `app-${version}-windows-x64.exe`,
            file_size_human: "25.6 MB",
            file_hash: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            download_url: "#",
          },
          {
            id: 2,
            architecture: "macOS x64",
            filename: `app-${version}-macos-x64.dmg`,
            file_size_human: "22.4 MB",
            file_hash: "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7",
            download_url: "#",
          },
          {
            id: 3,
            architecture: "Linux x64",
            filename: `app-${version}-linux-x64.tar.gz`,
            file_size_human: "24.1 MB",
            file_hash: "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8",
            download_url: "#",
          },
        ];
      } catch (error) {
        ElMessage.error("获取文件列表失败");
      } finally {
        filesLoading.value = false;
      }
    };

    const handleDownload = (file) => {
      // 这里应该实现实际的文件下载逻辑
      ElMessage.success(`开始下载 ${file.filename}`);
      // 实际项目中，可以使用以下代码：
      // const link = document.createElement('a')
      // link.href = file.download_url
      // link.setAttribute('download', file.filename)
      // document.body.appendChild(link)
      // link.click()
      // document.body.removeChild(link)
    };

    const formatReleaseNote = (note) => {
      if (!note) return "-";
      // 将换行符转换为HTML换行标签
      return note.replace(/\n/g, "<br>");
    };

    const formatDateTime = (dateString) => {
      if (!dateString) return "-";
      const date = new Date(dateString);
      return date.toLocaleString("zh-CN", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const goToHome = () => {
      router.push("/login");
    };

    // 组件挂载
    onMounted(() => {
      fetchVersionInfo();
      fetchFiles();
    });

    return {
      loading,
      filesLoading,
      spaceInfo,
      versionInfo,
      fileList,
      version,
      handleDownload,
      formatReleaseNote,
      formatDateTime,
      goToHome,
    };
  },
};
</script>

<style lang="scss" scoped>
.public-download-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;

  .download-card {
    max-width: 800px;
    width: 100%;
    margin-bottom: 40px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;

        .logo {
          width: 40px;
          height: 40px;
          margin-right: 15px;
        }

        .title-info {
          h2 {
            margin: 0 0 5px;
            font-size: 24px;
            font-weight: 600;
            color: #303133;
          }

          .version {
            margin: 0;
            font-size: 16px;
            color: #606266;
          }
        }
      }
    }

    .version-info {
      margin-bottom: 30px;

      .info-item {
        margin-bottom: 15px;

        .label {
          font-weight: 600;
          color: #606266;
          margin-right: 10px;
        }

        .value {
          color: #303133;

          :deep(ul) {
            margin: 10px 0;
            padding-left: 20px;

            li {
              margin-bottom: 5px;
            }
          }
        }
      }
    }

    .download-section {
      h3 {
        margin-bottom: 20px;
        font-size: 18px;
        color: #303133;
      }
    }
  }

  .footer {
    text-align: center;
    color: #909399;
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .public-download-container {
    padding: 20px 10px;

    .download-card {
      .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
      }
    }
  }
}
</style>
