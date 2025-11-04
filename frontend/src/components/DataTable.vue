<template>
  <div class="data-table-container">
    <div class="table-header" v-if="showHeader">
      <div class="table-title">
        <slot name="title">
          <h3>{{ title }}</h3>
        </slot>
      </div>

      <div class="table-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <el-table
      :data="data"
      :loading="loading"
      :height="height"
      :max-height="maxHeight"
      :stripe="stripe"
      :border="border"
      :size="size"
      :fit="fit"
      :show-header="showTableHeader"
      :highlight-current-row="highlightCurrentRow"
      :current-row-key="currentRowKey"
      :row-class-name="rowClassName"
      :row-style="rowStyle"
      :cell-class-name="cellClassName"
      :cell-style="cellStyle"
      :header-row-class-name="headerRowClassName"
      :header-row-style="headerRowStyle"
      :header-cell-class-name="headerCellClassName"
      :header-cell-style="headerCellStyle"
      :lazy="lazy"
      :load="load"
      :tree-props="treeProps"
      @select="handleSelect"
      @select-all="handleSelectAll"
      @selection-change="handleSelectionChange"
      @cell-mouse-enter="handleCellMouseEnter"
      @cell-mouse-leave="handleCellMouseLeave"
      @cell-click="handleCellClick"
      @cell-dblclick="handleCellDblclick"
      @row-click="handleRowClick"
      @row-contextmenu="handleRowContextmenu"
      @row-dblclick="handleRowDblclick"
      @header-click="handleHeaderClick"
      @header-contextmenu="handleHeaderContextmenu"
      @sort-change="handleSortChange"
      @filter-change="handleFilterChange"
      @current-change="handleCurrentChange"
      @header-dragend="handleHeaderDragend"
      @expand-change="handleExpandChange"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="selection"
        type="selection"
        width="55"
        align="center"
        :reserve-selection="reserveSelection"
        :selectable="selectable"
      />

      <!-- 索引列 -->
      <el-table-column
        v-if="showIndex"
        type="index"
        width="60"
        align="center"
        :label="indexLabel"
        :index="indexMethod"
      />

      <!-- 展开列 -->
      <el-table-column v-if="expandable" type="expand" width="50" align="center">
        <template #default="props">
          <slot name="expand" :row="props.row" :$index="props.$index"></slot>
        </template>
      </el-table-column>

      <!-- 数据列 -->
      <template v-for="(column, index) in columns" :key="index">
        <el-table-column
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
          :min-width="column.minWidth"
          :fixed="column.fixed"
          :render-header="column.renderHeader"
          :sortable="column.sortable"
          :sort-method="column.sortMethod"
          :sort-by="column.sortBy"
          :sort-orders="column.sortOrders || ['ascending', 'descending', null]"
          :resizable="column.resizable !== false"
          :formatter="column.formatter"
          :show-overflow-tooltip="column.showOverflowTooltip !== false"
          :align="column.align || 'left'"
          :header-align="column.headerAlign || column.align || 'left'"
          :class-name="column.className"
          :label-class-name="column.labelClassName"
          :selectable="column.selectable"
          :reserve-selection="column.reserveSelection"
          :filters="column.filters"
          :filter-placement="column.filterPlacement"
          :filter-multiple="column.filterMultiple !== false"
          :filter-method="column.filterMethod"
          :filtered-value="column.filteredValue"
        >
          <template #default="scope">
            <slot
              :name="column.prop"
              :row="scope.row"
              :column="scope.column"
              :$index="scope.$index"
            >
              {{ scope.row[column.prop] }}
            </slot>
          </template>
        </el-table-column>
      </template>

      <!-- 操作列 -->
      <el-table-column
        v-if="$slots.operations || operations.length > 0"
        :label="operationsLabel"
        :width="operationsWidth"
        :fixed="operationsFixed"
        align="center"
      >
        <template #default="scope">
          <slot name="operations" :row="scope.row" :$index="scope.$index">
            <template v-for="(operation, index) in operations" :key="index">
              <el-button
                v-if="!operation.visible || operation.visible(scope.row)"
                :type="operation.type || 'primary'"
                :size="operation.size || 'small'"
                :icon="operation.icon"
                :disabled="operation.disabled && operation.disabled(scope.row)"
                :loading="operation.loading && operation.loading(scope.row)"
                :plain="operation.plain !== false"
                :round="operation.round"
                :circle="operation.circle"
                :autofocus="operation.autofocus"
                :native-type="operation.nativeType || 'button'"
                @click="handleOperationClick(operation, scope.row, scope.$index)"
              >
                {{ operation.label }}
              </el-button>
            </template>
          </slot>
        </template>
      </el-table-column>

      <!-- 空数据 -->
      <template #empty>
        <slot name="empty">
          <div class="empty-data">
            <el-empty :description="emptyText" :image="emptyImage" :image-size="emptyImageSize" />
          </div>
        </slot>
      </template>
    </el-table>

    <!-- 分页 -->
    <div class="table-footer" v-if="showPagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        :total="total"
        :layout="paginationLayout"
        :background="paginationBackground"
        :small="paginationSmall"
        :disabled="paginationDisabled"
        :hide-on-single-page="hideOnSinglePage"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, ref, watch } from 'vue'
import { ElTable, ElTableColumn, ElPagination, ElEmpty, ElButton } from 'element-plus'

export default defineComponent({
  name: 'DataTable',
  components: {
    ElTable,
    ElTableColumn,
    ElPagination,
    ElEmpty,
    ElButton,
  },
  props: {
    // 基础属性
    data: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: '',
    },
    showHeader: {
      type: Boolean,
      default: true,
    },

    // 表格属性
    height: [String, Number],
    maxHeight: [String, Number],
    stripe: {
      type: Boolean,
      default: false,
    },
    border: {
      type: Boolean,
      default: true,
    },
    size: {
      type: String,
      default: 'default',
    },
    fit: {
      type: Boolean,
      default: true,
    },
    showTableHeader: {
      type: Boolean,
      default: true,
    },
    highlightCurrentRow: {
      type: Boolean,
      default: false,
    },
    currentRowKey: [String, Number],
    rowClassName: [String, Function],
    rowStyle: [Object, Function],
    cellClassName: [String, Function],
    cellStyle: [Object, Function],
    headerRowClassName: [String, Function],
    headerRowStyle: [Object, Function],
    headerCellClassName: [String, Function],
    headerCellStyle: [Object, Function],
    lazy: {
      type: Boolean,
      default: false,
    },
    load: Function,
    treeProps: {
      type: Object,
      default: () => ({
        hasChildren: 'hasChildren',
        children: 'children',
      }),
    },

    // 选择列
    selection: {
      type: Boolean,
      default: false,
    },
    reserveSelection: {
      type: Boolean,
      default: false,
    },
    selectable: Function,

    // 索引列
    showIndex: {
      type: Boolean,
      default: false,
    },
    indexLabel: {
      type: String,
      default: '#',
    },
    indexMethod: Function,

    // 展开列
    expandable: {
      type: Boolean,
      default: false,
    },

    // 数据列
    columns: {
      type: Array,
      default: () => [],
    },

    // 操作列
    operations: {
      type: Array,
      default: () => [],
    },
    operationsLabel: {
      type: String,
      default: '操作',
    },
    operationsWidth: {
      type: [String, Number],
      default: '',
    },
    operationsFixed: {
      type: [String, Boolean],
      default: false,
    },

    // 空数据
    emptyText: {
      type: String,
      default: '暂无数据',
    },
    emptyImage: String,
    emptyImageSize: {
      type: Number,
      default: 120,
    },

    // 分页
    showPagination: {
      type: Boolean,
      default: true,
    },
    total: {
      type: Number,
      default: 0,
    },
    pageSize: {
      type: Number,
      default: 20,
    },
    currentPage: {
      type: Number,
      default: 1,
    },
    pageSizes: {
      type: Array,
      default: () => [10, 20, 50, 100],
    },
    paginationLayout: {
      type: String,
      default: 'total, sizes, prev, pager, next, jumper',
    },
    paginationBackground: {
      type: Boolean,
      default: true,
    },
    paginationSmall: {
      type: Boolean,
      default: false,
    },
    paginationDisabled: {
      type: Boolean,
      default: false,
    },
    hideOnSinglePage: {
      type: Boolean,
      default: false,
    },
  },
  emits: [
    'select',
    'select-all',
    'selection-change',
    'cell-mouse-enter',
    'cell-mouse-leave',
    'cell-click',
    'cell-dblclick',
    'row-click',
    'row-contextmenu',
    'row-dblclick',
    'header-click',
    'header-contextmenu',
    'sort-change',
    'filter-change',
    'current-change',
    'header-dragend',
    'expand-change',
    'size-change',
    'update:pageSize',
    'update:currentPage',
    'operation-click',
  ],
  setup(props, { emit }) {
    // 分页
    const currentPage = ref(props.currentPage)
    const pageSize = ref(props.pageSize)

    // 监听props变化
    watch(
      () => props.currentPage,
      val => {
        currentPage.value = val
      }
    )

    watch(
      () => props.pageSize,
      val => {
        pageSize.value = val
      }
    )

    // 处理分页变化
    const handleSizeChange = size => {
      pageSize.value = size
      emit('update:pageSize', size)
      emit('size-change', size)
    }

    const handleCurrentPageChange = page => {
      currentPage.value = page
      emit('update:currentPage', page)
      emit('current-change', page)
    }

    // 处理操作点击
    const handleOperationClick = (operation, row, index) => {
      if (operation.click) {
        operation.click(row, index)
      }
      emit('operation-click', { operation, row, index })
    }

    // 表格事件处理
    const handleSelect = (selection, row) => {
      emit('select', selection, row)
    }

    const handleSelectAll = selection => {
      emit('select-all', selection)
    }

    const handleSelectionChange = selection => {
      emit('selection-change', selection)
    }

    const handleCellMouseEnter = (row, column, cell, event) => {
      emit('cell-mouse-enter', row, column, cell, event)
    }

    const handleCellMouseLeave = (row, column, cell, event) => {
      emit('cell-mouse-leave', row, column, cell, event)
    }

    const handleCellClick = (row, column, cell, event) => {
      emit('cell-click', row, column, cell, event)
    }

    const handleCellDblclick = (row, column, cell, event) => {
      emit('cell-dblclick', row, column, cell, event)
    }

    const handleRowClick = (row, column, event) => {
      emit('row-click', row, column, event)
    }

    const handleRowContextmenu = (row, column, event) => {
      emit('row-contextmenu', row, column, event)
    }

    const handleRowDblclick = (row, column, event) => {
      emit('row-dblclick', row, column, event)
    }

    const handleHeaderClick = (column, event) => {
      emit('header-click', column, event)
    }

    const handleHeaderContextmenu = (column, event) => {
      emit('header-contextmenu', column, event)
    }

    const handleSortChange = obj => {
      emit('sort-change', obj)
    }

    const handleFilterChange = filters => {
      emit('filter-change', filters)
    }

    const handleCurrentChange = (currentRow, oldCurrentRow) => {
      emit('current-change', currentRow, oldCurrentRow)
    }

    const handleHeaderDragend = (newWidth, oldWidth, column, event) => {
      emit('header-dragend', newWidth, oldWidth, column, event)
    }

    const handleExpandChange = (row, expanded) => {
      emit('expand-change', row, expanded)
    }

    return {
      currentPage,
      pageSize,
      handleSizeChange,
      handleCurrentPageChange,
      handleOperationClick,
      handleSelect,
      handleSelectAll,
      handleSelectionChange,
      handleCellMouseEnter,
      handleCellMouseLeave,
      handleCellClick,
      handleCellDblclick,
      handleRowClick,
      handleRowContextmenu,
      handleRowDblclick,
      handleHeaderClick,
      handleHeaderContextmenu,
      handleSortChange,
      handleFilterChange,
      handleCurrentChange,
      handleHeaderDragend,
      handleExpandChange,
    }
  },
})
</script>

<style scoped>
.data-table-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.dark-theme .table-title h3 {
  color: #e5eaf3;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.table-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.empty-data {
  padding: 20px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-actions {
    margin-top: 12px;
    width: 100%;
    justify-content: flex-end;
  }

  .table-footer {
    justify-content: center;
  }
}
</style>
