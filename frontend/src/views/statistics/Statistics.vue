<template>
  <div class="statistics-container">
    <!-- 概览卡片 -->
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

    <!-- 图表区域 -->
    <div class="charts-container">
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

        <!-- 软件空间分布图 -->
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>软件空间分布</span>
              </div>
            </template>
            <div class="chart-container" ref="spaceChartRef"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <!-- 版本下载统计 -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>版本下载统计</span>
                <el-button type="primary" link @click="refreshVersionStats">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <div class="chart-container" ref="versionChartRef"></div>
          </el-card>
        </el-col>

        <!-- 软件空间排行 -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>软件空间排行</span>
                <el-button type="primary" link @click="refreshSpaceStats">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <div class="chart-container" ref="rankingChartRef"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 详细统计表格 -->
    <div class="tables-container">
      <el-row :gutter="20">
        <!-- 软件空间统计表 -->
        <el-col :xs="24">
          <el-card class="table-card">
            <template #header>
              <div class="card-header">
                <span>软件空间统计</span>
                <div class="card-header-right">
                  <el-button type="primary" @click="exportSpaceStats">
                    <el-icon><Download /></el-icon>
                    导出
                  </el-button>
                </div>
              </div>
            </template>

            <el-table
              v-loading="spaceTableLoading"
              :data="spaceStatsTable"
              border
              style="width: 100%"
            >
              <el-table-column type="index" label="#" width="60" />
              <el-table-column prop="space_id" label="空间ID" min-width="120" />
              <el-table-column
                prop="space_name"
                label="空间名称"
                min-width="150"
              />
              <el-table-column
                prop="total_downloads"
                label="下载次数"
                width="120"
              />
              <el-table-column
                prop="versions_count"
                label="版本数量"
                width="120"
              />
              <el-table-column
                prop="latest_version"
                label="最新版本"
                min-width="120"
              />
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="spacePagination.page"
                v-model:page-size="spacePagination.size"
                :page-sizes="[10, 20, 50, 100]"
                :total="spacePagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSpaceSizeChange"
                @current-change="handleSpaceCurrentChange"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick, watch } from "vue";
import { useStore } from "vuex";
import { ElMessage } from "element-plus";
import * as echarts from "echarts";

export default {
  name: "StatisticsView",
  setup() {
    const store = useStore();

    // 响应式数据
    const loading = ref(false);
    const spaceTableLoading = ref(false);
    const downloadChartRef = ref(null);
    const spaceChartRef = ref(null);
    const versionChartRef = ref(null);
    const rankingChartRef = ref(null);
    const downloadChartPeriod = ref("7");

    // 图表实例
    let downloadChart = null;
    let spaceChart = null;
    let versionChart = null;
    let rankingChart = null;

    // 分页数据
    const spacePagination = reactive({
      page: 1,
      size: 10,
      total: 0,
    });

    // 计算属性
    const systemStats = computed(() => store.state.statistics.systemStats);
    const spaceStats = computed(() => store.state.statistics.spaceStats);
    const dailyDownloadStats = computed(
      () => store.state.statistics.dailyDownloadStats
    );
    const versionDownloadStats = computed(
      () => store.state.statistics.versionDownloadStats
    );
    const spaceStatsTable = computed(() => {
      const start = (spacePagination.page - 1) * spacePagination.size;
      const end = start + spacePagination.size;
      return spaceStats.value.slice(start, end);
    });
    const topDownloadedSpaces = computed(
      () => store.getters["statistics/topDownloadedSpaces"]
    );

    // 方法
    const fetchAllStatistics = async () => {
      loading.value = true;
      try {
        await store.dispatch("statistics/fetchAllStatistics");

        // 更新分页总数
        spacePagination.total = spaceStats.value.length;

        // 初始化图表
        nextTick(() => {
          initCharts();
        });
      } catch (error) {
        ElMessage.error("获取统计数据失败");
      } finally {
        loading.value = false;
      }
    };

    const initCharts = () => {
      initDownloadChart();
      initSpaceChart();
      initVersionChart();
      initRankingChart();
    };

    const initDownloadChart = () => {
      if (!downloadChartRef.value) return;

      downloadChart = echarts.init(downloadChartRef.value);

      const dates = dailyDownloadStats.value.map((item) => item.date);
      const downloads = dailyDownloadStats.value.map((item) => item.downloads);

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

    const initSpaceChart = () => {
      if (!spaceChartRef.value) return;

      spaceChart = echarts.init(spaceChartRef.value);

      const topSpaces = topDownloadedSpaces.value.slice(0, 10);
      const names = topSpaces.map((space) => space.space_name);
      const downloads = topSpaces.map((space) => space.total_downloads);

      const option = {
        tooltip: {
          trigger: "item",
          formatter: "{a} <br/>{b} : {c} ({d}%)",
        },
        legend: {
          orient: "vertical",
          left: "left",
          data: names,
        },
        series: [
          {
            name: "下载次数",
            type: "pie",
            radius: "55%",
            center: ["50%", "60%"],
            data: names.map((name, index) => ({
              value: downloads[index],
              name: name,
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
          },
        ],
      };

      spaceChart.setOption(option);
    };

    const initVersionChart = () => {
      if (!versionChartRef.value) return;

      versionChart = echarts.init(versionChartRef.value);

      const versions = versionDownloadStats.value.slice(0, 10);
      const names = versions.map((v) => v.version);
      const downloads = versions.map((v) => v.downloads);

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "value",
        },
        yAxis: {
          type: "category",
          data: names,
        },
        series: [
          {
            name: "下载次数",
            type: "bar",
            data: downloads,
            itemStyle: {
              color: "#67C23A",
            },
          },
        ],
      };

      versionChart.setOption(option);
    };

    const initRankingChart = () => {
      if (!rankingChartRef.value) return;

      rankingChart = echarts.init(rankingChartRef.value);

      const topSpaces = topDownloadedSpaces.value.slice(0, 5);
      const names = topSpaces.map((space) => space.space_name);
      const downloads = topSpaces.map((space) => space.total_downloads);

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "value",
        },
        yAxis: {
          type: "category",
          data: names,
        },
        series: [
          {
            name: "下载次数",
            type: "bar",
            data: downloads,
            itemStyle: {
              color: "#E6A23C",
            },
          },
        ],
      };

      rankingChart.setOption(option);
    };

    const resizeCharts = () => {
      downloadChart?.resize();
      spaceChart?.resize();
      versionChart?.resize();
      rankingChart?.resize();
    };

    const refreshVersionStats = async () => {
      try {
        await store.dispatch("statistics/fetchVersionDownloadStats");
        nextTick(() => {
          initVersionChart();
        });
        ElMessage.success("版本统计已刷新");
      } catch (error) {
        ElMessage.error("刷新版本统计失败");
      }
    };

    const refreshSpaceStats = async () => {
      try {
        await store.dispatch("statistics/fetchSpaceStats");
        nextTick(() => {
          initSpaceChart();
          initRankingChart();
        });
        ElMessage.success("空间统计已刷新");
      } catch (error) {
        ElMessage.error("刷新空间统计失败");
      }
    };

    const exportSpaceStats = () => {
      // 导出Excel
      const header = ["空间ID", "空间名称", "下载次数", "版本数量", "最新版本"];
      const rows = spaceStats.value.map((space) => [
        space.space_id,
        space.space_name,
        space.total_downloads,
        space.versions_count,
        space.latest_version,
      ]);

      let csvContent = header.join(",") + "\n";
      rows.forEach((row) => {
        csvContent += row.join(",") + "\n";
      });

      const blob = new Blob(["\ufeff" + csvContent], {
        type: "text/csv;charset=utf-8;",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute(
        "download",
        `space_stats_${new Date().toISOString().slice(0, 10)}.csv`
      );
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };

    const handleSpaceSizeChange = (size) => {
      spacePagination.size = size;
      spacePagination.page = 1;
    };

    const handleSpaceCurrentChange = (page) => {
      spacePagination.page = page;
    };

    // 监听窗口大小变化
    window.addEventListener("resize", resizeCharts);

    // 监听图表周期变化
    watch(downloadChartPeriod, () => {
      // 根据周期重新获取数据
      fetchAllStatistics();
    });

    // 组件卸载时清理
    const cleanup = () => {
      window.removeEventListener("resize", resizeCharts);
      downloadChart?.dispose();
      spaceChart?.dispose();
      versionChart?.dispose();
      rankingChart?.dispose();
    };

    // 执行清理函数
    cleanup();

    // 组件挂载
    onMounted(() => {
      fetchAllStatistics();
    });

    return {
      loading,
      spaceTableLoading,
      downloadChartRef,
      spaceChartRef,
      versionChartRef,
      rankingChartRef,
      downloadChartPeriod,
      systemStats,
      spaceStatsTable,
      spacePagination,
      refreshVersionStats,
      refreshSpaceStats,
      exportSpaceStats,
      handleSpaceSizeChange,
      handleSpaceCurrentChange,
    };
  },
};
</script>

<style lang="scss" scoped>
.statistics-container {
  padding: 20px;

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

  .charts-container {
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
  }

  .tables-container {
    .table-card {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .pagination-container {
        margin-top: 20px;
        display: flex;
        justify-content: center;
      }
    }
  }
}
</style>
