<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-title">仪表板</h2>
      <p class="dashboard-subtitle">欢迎使用 Forge 软件发布管理平台</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stats-card">
            <div class="stats-icon">
              <el-icon class="icon-box" color="#409EFF">
                <FolderOpened />
              </el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">
                {{ systemStats?.total_spaces || 0 }}
              </div>
              <div class="stats-label">软件空间</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="stats-card">
            <div class="stats-icon">
              <el-icon class="icon-box" color="#67C23A">
                <Document />
              </el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">
                {{ systemStats?.total_versions || 0 }}
              </div>
              <div class="stats-label">软件版本</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="stats-card">
            <div class="stats-icon">
              <el-icon class="icon-box" color="#E6A23C">
                <Download />
              </el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">
                {{ systemStats?.total_downloads || 0 }}
              </div>
              <div class="stats-label">总下载次数</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="stats-card">
            <div class="stats-icon">
              <el-icon class="icon-box" color="#F56C6C">
                <User />
              </el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">
                {{ systemStats?.active_users || 0 }}
              </div>
              <div class="stats-label">活跃用户</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 图表和列表区域 -->
    <div class="dashboard-content">
      <el-row :gutter="20">
        <!-- 下载趋势图 -->
        <el-col :xs="24" :lg="16">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>下载趋势</span>
                <div class="card-header-right">
                  <el-radio-group v-model="downloadChartPeriod" size="small">
                    <el-radio-button label="7">7天</el-radio-button>
                    <el-radio-button label="30">30天</el-radio-button>
                    <el-radio-button label="90">90天</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="chart-container" ref="downloadChartRef"></div>
          </el-card>
        </el-col>

        <!-- 热门软件空间 -->
        <el-col :xs="24" :lg="8">
          <el-card class="list-card">
            <template #header>
              <div class="card-header">
                <span>热门软件空间</span>
                <el-button type="primary" link @click="viewAllSpaces"
                  >查看全部</el-button
                >
              </div>
            </template>
            <div class="space-list">
              <div
                v-for="(space, index) in topSpaces"
                :key="space.space_id"
                class="space-item"
                @click="goToSpace(space.space_id)"
              >
                <div class="space-rank">{{ index + 1 }}</div>
                <div class="space-info">
                  <div class="space-name">{{ space.space_name }}</div>
                  <div class="space-meta">
                    <span class="space-downloads"
                      >{{ space.total_downloads }} 次下载</span
                    >
                    <span class="space-versions"
                      >{{ space.versions_count }} 个版本</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>最近活动</span>
            <el-button type="primary" link @click="viewAllActivities"
              >查看全部</el-button
            >
          </div>
        </template>
        <div class="activity-list">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-icon">
              <el-icon>
                <component :is="getActivityIcon(activity.type)" />
              </el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ formatTime(activity.time) }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import * as echarts from "echarts";

export default {
  name: "DashboardView",
  setup() {
    const store = useStore();
    const router = useRouter();

    // 响应式数据
    const downloadChartRef = ref(null);
    const downloadChartPeriod = ref("7");
    let downloadChart = null;

    // 计算属性
    const systemStats = computed(() => store.state.statistics.systemStats);
    const spaceStats = computed(() => store.state.statistics.spaceStats);
    const topSpaces = computed(
      () => store.getters["statistics/topDownloadedSpaces"]
    );

    // 模拟最近活动数据
    const recentActivities = ref([
      {
        id: 1,
        type: "upload",
        title: "用户admin上传了新版本v1.0.1",
        time: new Date(),
      },
      {
        id: 2,
        type: "download",
        title: "用户user1下载了软件A",
        time: new Date(Date.now() - 3600000),
      },
      {
        id: 3,
        type: "create",
        title: "用户admin创建了新软件空间B",
        time: new Date(Date.now() - 7200000),
      },
      {
        id: 4,
        type: "publish",
        title: "用户admin发布了版本v2.0.0",
        time: new Date(Date.now() - 10800000),
      },
    ]);

    // 方法
    const fetchDashboardData = async () => {
      try {
        await store.dispatch("statistics/fetchAllStatistics");
      } catch (error) {
        ElMessage.error("获取统计数据失败");
      }
    };

    const initDownloadChart = () => {
      if (!downloadChartRef.value) return;

      downloadChart = echarts.init(downloadChartRef.value);

      const dailyStats = store.state.statistics.dailyDownloadStats;
      const dates = dailyStats.map((item) => item.date);
      const downloads = dailyStats.map((item) => item.downloads);

      const option = {
        tooltip: {
          trigger: "axis",
        },
        legend: {
          data: ["下载量"],
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: dates,
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            name: "下载量",
            type: "line",
            stack: "Total",
            smooth: true,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "rgba(64, 158, 255, 0.5)" },
                { offset: 1, color: "rgba(64, 158, 255, 0.1)" },
              ]),
            },
            lineStyle: {
              color: "#409EFF",
            },
            itemStyle: {
              color: "#409EFF",
            },
            data: downloads,
          },
        ],
      };

      downloadChart.setOption(option);
    };

    const resizeChart = () => {
      if (downloadChart) {
        downloadChart.resize();
      }
    };

    const getActivityIcon = (type) => {
      const iconMap = {
        upload: "Upload",
        download: "Download",
        create: "Plus",
        publish: "Promotion",
      };
      return iconMap[type] || "InfoFilled";
    };

    const formatTime = (time) => {
      const now = new Date();
      const diff = now - new Date(time);
      const hours = Math.floor(diff / (1000 * 60 * 60));

      if (hours < 1) {
        return "刚刚";
      } else if (hours < 24) {
        return `${hours}小时前`;
      } else {
        const days = Math.floor(hours / 24);
        return `${days}天前`;
      }
    };

    const viewAllSpaces = () => {
      router.push("/space/list");
    };

    const viewAllActivities = () => {
      // 这里可以跳转到活动记录页面
      ElMessage.info("活动记录功能开发中");
    };

    const goToSpace = (spaceId) => {
      router.push(`/space/edit/${spaceId}`);
    };

    // 监听窗口大小变化
    window.addEventListener("resize", resizeChart);

    // 组件挂载
    onMounted(async () => {
      await fetchDashboardData();

      nextTick(() => {
        initDownloadChart();
      });
    });

    return {
      downloadChartRef,
      downloadChartPeriod,
      systemStats,
      spaceStats,
      topSpaces,
      recentActivities,
      getActivityIcon,
      formatTime,
      viewAllSpaces,
      viewAllActivities,
      goToSpace,
    };
  },
};
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;

  .dashboard-header {
    margin-bottom: 30px;

    .dashboard-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 10px;
    }

    .dashboard-subtitle {
      font-size: 14px;
      color: #606266;
      margin: 0;
    }
  }

  .stats-cards {
    margin-bottom: 20px;

    .stats-card {
      background: #fff;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      height: 100%;

      .stats-icon {
        margin-right: 20px;

        .icon-box {
          font-size: 32px;
        }
      }

      .stats-info {
        .stats-number {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
          line-height: 1;
          margin-bottom: 5px;
        }

        .stats-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .dashboard-content {
    margin-bottom: 20px;

    .chart-card {
      height: 400px;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .chart-container {
        width: 100%;
        height: 320px;
      }
    }

    .list-card {
      height: 400px;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .space-list {
        height: calc(100% - 56px);
        overflow-y: auto;

        .space-item {
          display: flex;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #ebeef5;
          cursor: pointer;

          &:last-child {
            border-bottom: none;
          }

          &:hover {
            background-color: #f5f7fa;
          }

          .space-rank {
            width: 24px;
            height: 24px;
            background-color: #f5f7fa;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: #909399;
            margin-right: 12px;
          }

          .space-info {
            flex: 1;

            .space-name {
              font-size: 14px;
              color: #303133;
              margin-bottom: 5px;
            }

            .space-meta {
              display: flex;
              font-size: 12px;
              color: #909399;

              .space-downloads {
                margin-right: 10px;
              }
            }
          }
        }
      }
    }
  }

  .recent-activities {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .activity-list {
      .activity-item {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #ebeef5;

        &:last-child {
          border-bottom: none;
        }

        .activity-icon {
          width: 32px;
          height: 32px;
          background-color: #f5f7fa;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 12px;

          .el-icon {
            color: #409eff;
          }
        }

        .activity-content {
          flex: 1;

          .activity-title {
            font-size: 14px;
            color: #303133;
            margin-bottom: 5px;
          }

          .activity-time {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }
  }
}
</style>
