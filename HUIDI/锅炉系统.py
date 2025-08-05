import sys
import os
import shutil
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu # Added QMenu import


class ImageViewerDialog(QDialog):
    """圖片查看器對話框"""
    def __init__(self, image_paths, current_index=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("圖片查看器")
        self.setModal(True)
        self.setGeometry(100, 100, 800, 600)
        
        # 保存图片路径列表和当前索引
        self.image_paths = image_paths if isinstance(image_paths, list) else [image_paths]
        self.current_index = current_index
        
        layout = QVBoxLayout()
        
        # 圖片顯示區域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(600, 400)
        layout.addWidget(self.image_label)
        
        # 導航按鈕區域
        nav_layout = QHBoxLayout()
        
        # 上一張按鈕
        self.prev_btn = QPushButton("◀ 上一张")
        self.prev_btn.clicked.connect(self.show_previous_image)
        self.prev_btn.setEnabled(len(self.image_paths) > 1)
        nav_layout.addWidget(self.prev_btn)
        
        # 圖片信息標籤
        self.image_info_label = QLabel()
        self.image_info_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.image_info_label)
        
        # 下一張按鈕
        self.next_btn = QPushButton("下一张 ▶")
        self.next_btn.clicked.connect(self.show_next_image)
        self.next_btn.setEnabled(len(self.image_paths) > 1)
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
        # 關閉按鈕
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # 載入當前圖片
        self.load_current_image()
    
    def load_current_image(self):
        """载入当前索引的圖片"""
        try:
            if 0 <= self.current_index < len(self.image_paths):
                image_path = self.image_paths[self.current_index]
                
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # 計算適合視窗的大小
                        scaled_pixmap = pixmap.scaled(
                            self.image_label.size(), 
                            Qt.KeepAspectRatio, 
                            Qt.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                        
                        # 更新圖片信息
                        filename = os.path.basename(image_path)
                        self.image_info_label.setText(f"{self.current_index + 1} / {len(self.image_paths)} - {filename}")
                        
                        # 更新按鈕狀態
                        self.prev_btn.setEnabled(self.current_index > 0)
                        self.next_btn.setEnabled(self.current_index < len(self.image_paths) - 1)
                        
                        print(f"成功載入圖片查看器: {image_path}")
                    else:
                        self.image_label.setText("無法載入圖片")
                        self.image_info_label.setText("圖片載入失敗")
                        print(f"圖片查看器載入失敗: {image_path}")
                else:
                    self.image_label.setText("圖片文件不存在")
                    self.image_info_label.setText("文件不存在")
                    print(f"圖片查看器文件不存在: {image_path}")
            else:
                self.image_label.setText("無效的圖片索引")
                self.image_info_label.setText("索引錯誤")
        except Exception as e:
            self.image_label.setText("載入圖片時發生錯誤")
            self.image_info_label.setText("載入錯誤")
            print(f"圖片查看器載入錯誤: {str(e)}")
            QMessageBox.critical(self, "圖片載入錯誤", f"載入圖片時發生錯誤:\n{str(e)}")
    
    def show_previous_image(self):
        """顯示上一張圖片"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
    
    def show_next_image(self):
        """顯示下一張圖片"""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.load_current_image()


class ImageThumbnailWidget(QWidget):
    """圖片縮略圖小部件"""
    def __init__(self, image_path, image_list=None, current_index=0, parent=None, delete_callback=None):
        super().__init__(parent)
        self.image_path = image_path
        self.image_list = image_list if image_list else [image_path]
        self.current_index = current_index
        self.delete_callback = delete_callback  # 添加删除回调函数
        self.setFixedSize(120, 120)
        self.setStyleSheet("border: 1px solid #ccc; margin: 2px;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 縮略圖標籤
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFixedSize(116, 116)
        
        # 載入縮略圖
        try:
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(116, 116, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.thumbnail_label.setPixmap(scaled_pixmap)
                    print(f"成功載入縮略圖: {image_path}")
                else:
                    self.thumbnail_label.setText("載入失敗")
                    print(f"圖片載入失敗: {image_path}")
            else:
                self.thumbnail_label.setText("文件不存在")
                print(f"圖片文件不存在: {image_path}")
        except Exception as e:
            self.thumbnail_label.setText("載入錯誤")
            print(f"載入圖片時發生錯誤 {image_path}: {str(e)}")
        
        layout.addWidget(self.thumbnail_label)
        self.setLayout(layout)
        
        # 設置滑鼠事件
        self.setMouseTracking(True)
        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        if self.delete_callback:
            menu = QMenu(self)
            delete_action = QAction("删除图片", self)
            delete_action.triggered.connect(lambda: self.delete_callback(self.image_path, self.current_index))
            menu.addAction(delete_action)
            menu.exec_(self.mapToGlobal(position))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            try:
                # 檢查圖片文件是否存在
                if not os.path.exists(self.image_path):
                    QMessageBox.warning(self, "錯誤", f"圖片文件不存在: {self.image_path}")
                    return
                
                # 验证文件是否可读
                if not os.access(self.image_path, os.R_OK):
                    QMessageBox.warning(self, "文件权限错误", f"无法读取图片文件:\n{self.image_path}")
                    return
                
                # 验证文件大小
                file_size = os.path.getsize(self.image_path)
                if file_size == 0:
                    QMessageBox.warning(self, "文件错误", f"图片文件为空:\n{self.image_path}")
                    return
                
                print(f"打開圖片查看器: {self.image_path}")
                # 打開圖片查看器，傳遞圖片列表和當前索引
                dialog = ImageViewerDialog(self.image_list, self.current_index, self.parent())
                dialog.exec_()
            except Exception as e:
                print(f"打開圖片查看器失敗: {str(e)}")
                QMessageBox.warning(self, "錯誤", f"無法打開圖片: {str(e)}")
    
    def enterEvent(self, event):
        self.setStyleSheet("border: 2px solid #0078d4; margin: 2px; cursor: pointer;")
    
    def leaveEvent(self, event):
        self.setStyleSheet("border: 1px solid #ccc; margin: 2px;")


class PriceSearchImageWidget(QWidget):
    """价格搜索结果中的图片显示组件"""
    def __init__(self, image_filenames, images_dir, parent=None):
        super().__init__(parent)
        self.image_filenames = image_filenames
        self.images_dir = images_dir
        
        # 设置固定大小 - 调整为更适合表格单元格的大小
        self.setFixedSize(150, 50)
        
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        if image_filenames:
            print(f"PriceSearchImageWidget: 处理 {len(image_filenames)} 张图片")
            # 显示前3张图片的缩略图
            for i, filename in enumerate(image_filenames[:3]):
                try:
                    image_path = os.path.join(self.images_dir, filename)
                    print(f"PriceSearchImageWidget: 检查图片路径 {image_path}, 存在: {os.path.exists(image_path)}")
                    if os.path.exists(image_path):
                        thumbnail = QLabel()
                        thumbnail.setFixedSize(40, 40)
                        thumbnail.setAlignment(Qt.AlignCenter)
                        thumbnail.setStyleSheet("border: 1px solid #ccc; border-radius: 2px;")
                        
                        # 加载并缩放图片
                        pixmap = QPixmap(image_path)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            thumbnail.setPixmap(scaled_pixmap)
                            print(f"PriceSearchImageWidget: 成功加载图片 {filename}")
                        else:
                            thumbnail.setText("❌")
                            thumbnail.setStyleSheet("border: 1px solid #ccc; border-radius: 2px; color: red; font-size: 10px;")
                    else:
                        thumbnail = QLabel("❌")
                        thumbnail.setFixedSize(40, 40)
                        thumbnail.setAlignment(Qt.AlignCenter)
                        thumbnail.setStyleSheet("border: 1px solid #ccc; border-radius: 2px; color: red; font-size: 10px;")
                    
                    layout.addWidget(thumbnail)
                except Exception as e:
                    print(f"创建缩略图失败 {filename}: {e}")
                    thumbnail = QLabel("❌")
                    thumbnail.setFixedSize(40, 40)
                    thumbnail.setAlignment(Qt.AlignCenter)
                    thumbnail.setStyleSheet("border: 1px solid #ccc; border-radius: 2px; color: red; font-size: 10px;")
                    layout.addWidget(thumbnail)
            
            # 如果图片超过3张，显示更多提示
            if len(image_filenames) > 3:
                more_label = QLabel(f"+{len(image_filenames) - 3}")
                more_label.setFixedSize(40, 40)
                more_label.setAlignment(Qt.AlignCenter)
                more_label.setStyleSheet("border: 1px solid #ccc; border-radius: 2px; background-color: #f0f0f0; color: #666; font-size: 10px;")
                layout.addWidget(more_label)
        else:
            # 没有图片时显示提示
            print("PriceSearchImageWidget: 没有图片文件")
            no_image_label = QLabel("无图片")
            no_image_label.setFixedSize(100, 40)
            no_image_label.setAlignment(Qt.AlignCenter)
            no_image_label.setStyleSheet("border: 1px solid #ccc; border-radius: 2px; color: #999; font-size: 10px;")
            layout.addWidget(no_image_label)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """显示右键菜单"""
        if self.image_filenames:
            menu = QMenu(self)
            
            # 查看所有图片
            view_action = menu.addAction("查看所有图片")
            view_action.triggered.connect(self.view_all_images)
            
            menu.exec_(self.mapToGlobal(position))
    
    def view_all_images(self):
        """查看所有图片"""
        try:
            image_paths = []
            for filename in self.image_filenames:
                image_path = os.path.join(self.images_dir, filename)
                if os.path.exists(image_path):
                    image_paths.append(image_path)
            
            if image_paths:
                dialog = ImageViewerDialog(image_paths, 0, self)
                dialog.exec_()
            else:
                QMessageBox.information(self, "提示", "没有可查看的图片")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查看图片失败: {str(e)}")
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton and self.image_filenames:
            self.view_all_images()
        super().mousePressEvent(event)


class BoilerKnowledge(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("锅炉知识管理系统 - 专业版")
        self.setGeometry(100, 100, 1600, 900)

        # 创建存储目录 - 改为桌面上的指定文件夹
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.storage_dir = os.path.join(desktop_path, "锅炉知识管理系统安装包", "锅炉系统文件")
        self.images_dir = os.path.join(self.storage_dir, "图片")
        self.data_dir = os.path.join(self.storage_dir, "数据")
        self.create_storage_directories()

        # 初始化图片路径变量
        self.current_image_paths = []
        self.current_principle_image_paths = []
        self.current_supplier_image_paths = []

        # 初始化当前选中项为None
        self.current_item = None
        
        # 添加初始化标志，防止在初始化过程中触发自动保存
        self._initializing = True

        # 加载或初始化数据
        self.load_data()

        # 创建主界面
        self.create_ui()
        
        # 初始化树形结构
        self.init_tree()
        
        # 初始化标签索引
        self.update_tag_index()
        
        # 设置自动保存（在UI创建完成后）
        self.setup_auto_save()
        
        # 设置零部件自动保存
        self.setup_parts_auto_save()
        
        # 初始化完成，允许自动保存
        self._initializing = False
        
        # 集成稳定性优化器
        try:
            from stability_optimization import integrate_stability_optimizer
            self.stability_optimizer = integrate_stability_optimizer(self)
            print("稳定性优化器已成功集成")
        except Exception as e:
            print(f"稳定性优化器集成失败: {e}")
            self.stability_optimizer = None
    
    def setup_auto_save(self):
        """设置自动保存功能"""
        # 基本信息自动保存
        if hasattr(self, 'content_edit'):
            self.content_edit.textChanged.connect(self.auto_save_content)
        if hasattr(self, 'tags_edit'):
            self.tags_edit.textChanged.connect(self.auto_save_tags)
        
        # 技术参数自动保存
        if hasattr(self, 'tech_table'):
            self.tech_table.itemChanged.connect(self.auto_save_tech_params)
        
        # 价格信息自动保存
        if hasattr(self, 'base_price_edit'):
            self.base_price_edit.textChanged.connect(self.auto_save_pricing)
        if hasattr(self, 'currency_combo'):
            self.currency_combo.currentTextChanged.connect(self.auto_save_pricing)
        if hasattr(self, 'supplier_table'):
            self.supplier_table.itemChanged.connect(self.auto_save_pricing)
        
        # 维护信息自动保存
        if hasattr(self, 'cycle_edit'):
            self.cycle_edit.textChanged.connect(self.auto_save_maintenance)
        if hasattr(self, 'procedures_edit'):
            self.procedures_edit.textChanged.connect(self.auto_save_maintenance)
        if hasattr(self, 'notes_edit'):
            self.notes_edit.textChanged.connect(self.auto_save_maintenance)
    
    def auto_save_content(self):
        """自动保存内容"""
        try:
            # 检查是否正在初始化
            if hasattr(self, '_initializing') and self._initializing:
                return
                
            if not self.current_item:
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                return
                
            data = self.get_data_by_path(path)
            if not data or "children" in data:
                return
                
            data["content"] = self.content_edit.toPlainText()
            self.save_data()
            print("内容已自动保存")
        except Exception as e:
            print(f"自动保存内容失败: {str(e)}")
    
    def auto_save_tags(self):
        """自动保存标签"""
        try:
            # 检查是否正在初始化
            if hasattr(self, '_initializing') and self._initializing:
                return
                
            if not self.current_item:
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                return
                
            data = self.get_data_by_path(path)
            if not data or "children" in data:
                return
                
            tags_text = self.tags_edit.text().strip()
            if tags_text:
                tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
                data["tags"] = tags
            else:
                data["tags"] = []
            
            self.update_tag_index()
            self.save_data()
            print("标签已自动保存")
        except Exception as e:
            print(f"自动保存标签失败: {str(e)}")
    
    def auto_save_tech_params(self):
        """自动保存技术参数"""
        try:
            # 检查是否正在初始化
            if hasattr(self, '_initializing') and self._initializing:
                return
                
            if not self.current_item:
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                return
                
            data = self.get_data_by_path(path)
            if not data or "children" in data:
                return
            
            # 获取表格数据
            params = {}
            for row in range(self.tech_table.rowCount()):
                name_item = self.tech_table.item(row, 0)
                value_item = self.tech_table.item(row, 1)
                if name_item and value_item:
                    name = name_item.text().strip()
                    value = value_item.text().strip()
                    if name:
                        params[name] = value
            
            data["tech_params"] = params
            self.save_data()
            print("技术参数已自动保存")
        except Exception as e:
            print(f"自动保存技术参数失败: {str(e)}")
    
    def auto_save_pricing(self):
        """自动保存价格信息"""
        try:
            # 检查是否正在初始化
            if hasattr(self, '_initializing') and self._initializing:
                print("自动保存价格信息: 正在初始化，跳过")
                return
                
            # 确保 current_item 属性存在
            if not hasattr(self, 'current_item'):
                print("自动保存价格信息: current_item 属性不存在")
                return
                
            if not self.current_item:
                print("自动保存价格信息: 没有选中项目")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                print("自动保存价格信息: 无法获取项目路径")
                return
                
            data = self.get_data_by_path(path)
            if not data or "children" in data:
                print("自动保存价格信息: 数据无效或为分类")
                return
            
            print(f"自动保存价格信息: 开始处理项目 {' > '.join(path)}")
            
            # 获取基础价格
            base_price_text = self.base_price_edit.text().strip()
            try:
                base_price = float(base_price_text) if base_price_text else 0
            except ValueError:
                base_price = 0
            currency = self.currency_combo.currentText()
            
            # 获取现有供应商数据以保留图片信息
            existing_suppliers = data.get("pricing", {}).get("suppliers", [])
            print(f"现有供应商数量: {len(existing_suppliers)}")
            
            # 获取供应商信息
            suppliers = []
            print(f"开始处理供应商表格，共 {self.supplier_table.rowCount()} 行")
            for row in range(self.supplier_table.rowCount()):
                try:
                    supplier = {}
                    for col in range(self.supplier_table.columnCount()):
                        item = self.supplier_table.item(row, col)
                        if item:
                            if col == 0:  # 型号（暂时不保存）
                                pass
                            elif col == 1:  # 供应商名称
                                supplier["name"] = item.text().strip()
                            elif col == 2:  # 价格
                                price_text = item.text().strip()
                                try:
                                    supplier["price"] = float(price_text) if price_text else 0
                                except ValueError:
                                    supplier["price"] = 0
                            elif col == 3:  # 供货周期
                                supplier["lead_time"] = item.text().strip()
                            elif col == 4:  # 联系方式
                                supplier["contact"] = item.text().strip()
                            elif col == 5:  # 产品图片（仅显示用，不保存到数据）
                                pass  # 图片信息通过其他方式管理
                        else:
                            # 如果单元格为空，设置默认值
                            if col == 0:  # 型号（暂时不保存）
                                pass
                            elif col == 1:  # 供应商名称
                                supplier["name"] = ""
                            elif col == 2:  # 价格
                                supplier["price"] = 0
                            elif col == 3:  # 供货周期
                                supplier["lead_time"] = ""
                            elif col == 4:  # 联系方式
                                supplier["contact"] = ""
                            elif col == 5:  # 产品图片（仅显示用，不保存到数据）
                                pass  # 图片信息通过其他方式管理
                    
                    if supplier.get("name"):  # 只保存有供应商名称的行
                        # 保留现有供应商的图片信息
                        supplier["images"] = []
                        for existing_supplier in existing_suppliers:
                            if existing_supplier.get("name") == supplier["name"]:
                                supplier["images"] = existing_supplier.get("images", [])
                                print(f"自动保存时保留供应商 '{supplier['name']}' 的 {len(supplier['images'])} 张图片")
                                break
                        
                        suppliers.append(supplier)
                        print(f"添加供应商: {supplier['name']} - 价格: {supplier.get('price', 0)}")
                    else:
                        print(f"跳过第 {row} 行，供应商名称为空")
                except Exception as row_error:
                    print(f"处理第 {row} 行供应商数据时出错: {str(row_error)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"总共保存 {len(suppliers)} 个供应商")
            
            # 更新数据
            if "pricing" not in data:
                data["pricing"] = {}
            
            data["pricing"]["base_price"] = base_price
            data["pricing"]["currency"] = currency
            data["pricing"]["suppliers"] = suppliers
            
            self.save_data()
            print("价格信息已自动保存")
            # 可选：在状态栏显示保存状态（如果存在状态栏）
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(f"供应商信息已自动保存 ({len(suppliers)} 个供应商)", 3000)
        except Exception as e:
            error_msg = f"自动保存价格信息失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            # 可选：在状态栏显示错误（如果存在状态栏）
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(error_msg, 5000)
    
    def auto_save_maintenance(self):
        """自动保存维护信息"""
        try:
            # 检查是否正在初始化
            if hasattr(self, '_initializing') and self._initializing:
                return
                
            if not self.current_item:
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                return
                
            data = self.get_data_by_path(path)
            if not data or "children" in data:
                return
            
            # 获取维护信息
            maintenance = {
                "cycle": self.cycle_edit.text().strip(),
                "procedures": self.procedures_edit.toPlainText().strip(),
                "notes": self.notes_edit.toPlainText().strip()
            }
            
            data["maintenance"] = maintenance
            self.save_data()
            print("维护信息已自动保存")
        except Exception as e:
            print(f"自动保存维护信息失败: {str(e)}")
    
    def delete_image_callback(self, image_path, current_index):
        """删除图片回调函数"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
            
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
            
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
            
            # 确认删除
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除这张图片吗？\n{os.path.basename(image_path)}",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            
            # 从数据中移除图片引用
            image_filename = os.path.basename(image_path)
            if "images" in data and image_filename in data["images"]:
                data["images"].remove(image_filename)
                print(f"已从数据中移除图片引用: {image_filename}")
            
            # 删除物理文件
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"已删除图片文件: {image_path}")
            
            # 保存数据
            self.save_data()
            
            # 重新加载图片显示
            self.load_content(self.current_item)
            
            QMessageBox.information(self, "成功", "图片已删除！")
        except Exception as e:
            error_msg = f"删除图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "删除失败", error_msg)
    
    def delete_principle_image_callback(self, image_path, current_index):
        """删除原理图片回调函数"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
            
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
            
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
            
            # 确认删除
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除这张原理图片吗？\n{os.path.basename(image_path)}",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            
            # 从数据中移除图片引用
            image_filename = os.path.basename(image_path)
            if "principle_images" in data and image_filename in data["principle_images"]:
                data["principle_images"].remove(image_filename)
                print(f"已从数据中移除原理图片引用: {image_filename}")
            
            # 删除物理文件
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"已删除原理图片文件: {image_path}")
            
            # 保存数据
            self.save_data()
            
            # 重新加载图片显示
            self.load_content(self.current_item)
            
            QMessageBox.information(self, "成功", "原理图片已删除！")
        except Exception as e:
            error_msg = f"删除原理图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "删除失败", error_msg)
    
    def delete_supplier_image_callback(self, image_path, current_index):
        """删除供应商图片回调函数"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
            
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
            
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
            
            # 获取当前选中的供应商行
            supplier_row = self.get_current_supplier_row()
            if supplier_row is None:
                QMessageBox.warning(self, "警告", "请先选择供应商！")
                return
            
            # 确认删除
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除这张供应商图片吗？\n{os.path.basename(image_path)}",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            
            # 从供应商数据中移除图片引用
            image_filename = os.path.basename(image_path)
            if "pricing" in data and "suppliers" in data["pricing"]:
                suppliers = data["pricing"]["suppliers"]
                if supplier_row < len(suppliers):
                    supplier = suppliers[supplier_row]
                    if "images" in supplier and image_filename in supplier["images"]:
                        supplier["images"].remove(image_filename)
                        print(f"已从供应商数据中移除图片引用: {image_filename}")
            
            # 删除物理文件
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"已删除供应商图片文件: {image_path}")
            
            # 保存数据
            self.save_data()
            
            # 重新加载供应商图片显示
            self.load_supplier_images_for_specific_supplier(supplier_row)
            
            # 更新供应商表格中的图片数量显示
            self.load_pricing(data.get("pricing", {}))
            
            QMessageBox.information(self, "成功", "供应商图片已删除！")
        except Exception as e:
            error_msg = f"删除供应商图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "删除失败", error_msg)

    def create_storage_directories(self):
        """创建存储目录"""
        try:
            print(f"正在创建存储目录...")
            print(f"存储根目录: {self.storage_dir}")
            print(f"图片目录: {self.images_dir}")
            print(f"数据目录: {self.data_dir}")
            
            for dir_path in [self.storage_dir, self.images_dir, self.data_dir]:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"已创建目录: {dir_path}")
                else:
                    print(f"目录已存在: {dir_path}")
                    
            # 验证目录是否可写
            for dir_path in [self.storage_dir, self.images_dir, self.data_dir]:
                if not os.access(dir_path, os.W_OK):
                    raise Exception(f"目录无写入权限: {dir_path}")
                    
            print(f"存储目录已准备就绪: {self.storage_dir}")
        except Exception as e:
            error_msg = f"创建存储目录失败: {e}"
            print(error_msg)
            QMessageBox.critical(self, "目录创建失败", error_msg)

    def load_data(self):
        """加载数据"""
        self.data_file = os.path.join(self.data_dir, "system_data.json")
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.system_data = json.load(f)
                print(f"数据已从以下位置加载: {self.data_file}")
            else:
                print(f"未找到现有数据文件，将创建新的数据文件: {self.data_file}")
                # 初始化默认数据结构
                self.system_data = {
                    "categories": {
                        "锅炉系统": {
                            "children": {
                                "给料系统": {
                                    "children": {
                                        "皮带": {
                                            "content": "皮带是一条皮带\n",
                                            "tags": ["给料系统", "输送设备"],
                                            "images": [],
                                            "technical_params": {
                                                "型号": "B800",
                                                "长度": "50m",
                                                "材质": "橡胶",
                                                "功率": "5.5kW"
                                            },
                                            "pricing": {
                                                "base_price": 15000,
                                                "currency": "CNY",
                                                "suppliers": [
                                                    {
                                                        "name": "上海输送设备厂",
                                                        "price": 15000,
                                                        "lead_time": "7天",
                                                        "contact": "张经理 13800138000"
                                                    }
                                                ]
                                            },
                                            "maintenance": {
                                                "cycle": "每月检查",
                                                "procedures": "检查皮带张力、清理杂物",
                                                "notes": "注意防止跑偏"
                                            },
                                            "parts": []
                                        },
                                        "给料机": {
                                            "content": "",
                                            "tags": ["给料系统", "输送设备"],
                                            "images": [],
                                            "technical_params": {},
                                            "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                                            "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                                            "parts": []
                                        }
                                    }
                                },
                                "燃烧系统": {
                                    "children": {
                                        "燃烧器": {
                                            "content": "",
                                            "tags": ["燃烧系统", "燃烧设备"],
                                            "images": [],
                                            "technical_params": {},
                                            "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                                            "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                                            "parts": []
                                        },
                                        "点火器": {
                                            "content": "",
                                            "tags": ["燃烧系统", "点火设备"],
                                            "images": [],
                                            "technical_params": {},
                                            "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                                            "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                                            "parts": []
                                        }
                                    }
                                },
                                "汽水系统": {
                                    "children": {
                                        "汽包": {
                                            "content": "",
                                            "tags": ["汽水系统", "压力容器"],
                                            "images": [],
                                            "technical_params": {},
                                            "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                                            "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                                            "parts": []
                                        },
                                        "水冷壁": {
                                            "content": "",
                                            "tags": ["汽水系统", "受热面"],
                                            "images": [],
                                            "technical_params": {},
                                            "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                                            "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                                            "parts": []
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "tags": {},  # 标签索引
                    "suppliers": {}  # 供应商信息
                }
                self.save_data()
        except Exception as e:
            error_msg = f"加载数据失败: {e}"
            print(error_msg)
            QMessageBox.critical(self, "数据加载失败", error_msg)
            self.system_data = {"categories": {}, "tags": {}, "suppliers": {}}

    def save_data(self):
        """保存数据"""
        try:
            # 确保数据目录存在
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.system_data, f, ensure_ascii=False, indent=2)
            print(f"数据已成功保存到: {self.data_file}")
        except Exception as e:
            error_msg = f"保存数据失败: {e}"
            print(error_msg)
            QMessageBox.critical(self, "保存失败", error_msg)

    def create_ui(self):
        """创建主界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧：功能模块选择区
        left_panel = QWidget()
        left_panel.setMaximumWidth(200)
        left_panel.setMinimumWidth(200)
        left_panel.setStyleSheet("background-color: #f0f0f0; border-right: 1px solid #ccc;")
        
        left_layout = QVBoxLayout()
        
        # 功能模块标题
        module_title = QLabel("功能模块")
        module_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px; border-bottom: 2px solid #0078d4;")
        left_layout.addWidget(module_title)
        
        # 功能模块按钮
        self.create_module_buttons(left_layout)
        
        # 添加弹性空间
        left_layout.addStretch()
        
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)
        
        # 右侧：工作区域
        self.work_area = QStackedWidget()
        self.work_area.setStyleSheet("background-color: white;")
        
        # 创建各个模块的工作区
        self.create_boiler_module()  # 锅炉系统登记模块
        self.create_patent_module()  # 知识产权管理模块
        self.create_calculation_module()  # 计算模板模块
        self.create_procurement_module()  # 采购模块
        
        main_layout.addWidget(self.work_area)
        
        central_widget.setLayout(main_layout)
        
        # 设置窗口属性
        self.setWindowTitle("锅炉管理系统 - 专业版")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化状态栏
        self.statusBar().showMessage("系统就绪", 3000)

    def create_module_buttons(self, layout):
        """创建功能模块按钮"""
        # 锅炉系统登记模块
        self.boiler_btn = QPushButton("锅炉系统登记")
        self.boiler_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.boiler_btn.clicked.connect(lambda: self.switch_module(0))
        layout.addWidget(self.boiler_btn)
        
        # 知识产权管理模块
        self.patent_btn = QPushButton("知识产权管理")
        self.patent_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
            }
            QPushButton:pressed {
                background-color: #0c5c0c;
            }
        """)
        self.patent_btn.clicked.connect(lambda: self.switch_module(1))
        layout.addWidget(self.patent_btn)
        
        # 计算模板模块
        self.calc_btn = QPushButton("计算模板")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #d83b01;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c13501;
            }
            QPushButton:pressed {
                background-color: #a52d01;
            }
        """)
        self.calc_btn.clicked.connect(lambda: self.switch_module(2))
        layout.addWidget(self.calc_btn)
        
        # 采购模块按钮
        self.procurement_btn = QPushButton("采购模块")
        self.procurement_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b69d6;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #5f5dc7;
            }
            QPushButton:pressed {
                background-color: #5351b8;
            }
        """)
        self.procurement_btn.clicked.connect(lambda: self.switch_module(3))
        layout.addWidget(self.procurement_btn)

    def switch_module(self, module_index):
        """切换功能模块"""
        self.work_area.setCurrentIndex(module_index)
        
        # 更新按钮状态
        buttons = [self.boiler_btn, self.patent_btn, self.calc_btn, self.procurement_btn]
        for i, btn in enumerate(buttons):
            if i == module_index:
                btn.setStyleSheet(btn.styleSheet().replace("background-color:", "background-color: #666;"))
            else:
                # 恢复原始颜色
                colors = ["#0078d4", "#107c10", "#d83b01", "#6b69d6"]
                btn.setStyleSheet(btn.styleSheet().replace("background-color: #666;", f"background-color: {colors[i]};"))
        
        # 更新状态栏
        module_names = ["锅炉系统登记", "知识产权管理", "计算模板", "采购模块"]
        self.statusBar().showMessage(f"当前模块: {module_names[module_index]}", 3000)

    def create_boiler_module(self):
        """创建锅炉系统登记模块"""
        boiler_widget = QWidget()
        boiler_layout = QHBoxLayout()
        
        # 左侧：树形结构
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_panel.setMinimumWidth(300)
        left_panel.setStyleSheet("background-color: #f8f9fa; border-right: 1px solid #dee2e6;")
        
        left_layout = QVBoxLayout()
        
        # 树形结构标题
        tree_title = QLabel("设备分类")
        tree_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; padding: 5px;")
        left_layout.addWidget(tree_title)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索设备...")
        self.search_input.textChanged.connect(self.search_by_tag)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.search_by_tag)
        search_layout.addWidget(self.search_btn)
        left_layout.addLayout(search_layout)
        
        # 搜索结果显示列表
        self.search_results = QListWidget()
        self.search_results.itemClicked.connect(self.select_search_result)
        self.search_results.setMaximumHeight(150)
        left_layout.addWidget(self.search_results)
        
        # 树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("设备分类")
        self.tree.itemClicked.connect(self.load_content)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.tree)
        
        # 树形操作按钮
        tree_btn_layout = QHBoxLayout()
        self.add_category_btn = QPushButton("添加分类")
        self.add_category_btn.clicked.connect(self.add_category)
        self.add_item_btn = QPushButton("添加设备")
        self.add_item_btn.clicked.connect(self.add_item)
        
        tree_btn_layout.addWidget(self.add_category_btn)
        tree_btn_layout.addWidget(self.add_item_btn)
        left_layout.addLayout(tree_btn_layout)
        
        left_panel.setLayout(left_layout)
        boiler_layout.addWidget(left_panel)
        
        # 右侧：标签页
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # 标签页控件
        self.tab_widget = QTabWidget()
        
        # 创建各个标签页
        self.basic_tab = QWidget()
        self.tech_tab = QWidget()
        self.price_tab = QWidget()
        self.maintenance_tab = QWidget()
        self.parts_tab = QWidget()  # 新增零部件附页标签页
        
        self.tab_widget.addTab(self.basic_tab, "基本信息")
        self.tab_widget.addTab(self.tech_tab, "技术参数")
        self.tab_widget.addTab(self.price_tab, "价格管理")
        self.tab_widget.addTab(self.maintenance_tab, "维护保养")
        self.tab_widget.addTab(self.parts_tab, "零部件附页")  # 新增标签页
        
        self.create_basic_tab()
        self.create_tech_tab()
        self.create_price_tab()
        self.create_maintenance_tab()
        self.create_parts_tab()  # 新增创建零部件附页标签页的方法
        
        right_layout.addWidget(self.tab_widget)
        right_panel.setLayout(right_layout)
        boiler_layout.addWidget(right_panel)
        
        boiler_widget.setLayout(boiler_layout)
        self.work_area.addWidget(boiler_widget)

    def create_patent_module(self):
        """创建知识产权管理模块"""
        patent_widget = QWidget()
        patent_layout = QVBoxLayout()
        
        # 模块标题
        title = QLabel("知识产权管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; padding: 10px;")
        patent_layout.addWidget(title)
        
        # 功能说明
        info = QLabel("专利管理登记功能正在开发中...\n\n功能包括：\n• 专利申请记录\n• 专利状态跟踪\n• 专利文档管理\n• 专利检索功能")
        info.setStyleSheet("font-size: 14px; color: #666; padding: 20px; background-color: #f8f9fa; border-radius: 8px;")
        info.setAlignment(Qt.AlignCenter)
        patent_layout.addWidget(info)
        
        # 添加弹性空间
        patent_layout.addStretch()
        
        patent_widget.setLayout(patent_layout)
        self.work_area.addWidget(patent_widget)

    def create_calculation_module(self):
        """创建计算模板模块"""
        calc_widget = QWidget()
        calc_layout = QVBoxLayout()
        
        # 模块标题
        title = QLabel("计算模板")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; padding: 10px;")
        calc_layout.addWidget(title)
        
        # 功能说明
        info = QLabel("Excel功能计算模板正在开发中...\n\n功能包括：\n• 数据插入和编辑\n• 公式计算\n• 模板管理\n• 数据导出")
        info.setStyleSheet("font-size: 14px; color: #666; padding: 20px; background-color: #f8f9fa; border-radius: 8px;")
        info.setAlignment(Qt.AlignCenter)
        calc_layout.addWidget(info)
        
        # 添加弹性空间
        calc_layout.addStretch()
        
        calc_widget.setLayout(calc_layout)
        self.work_area.addWidget(calc_widget)

    def create_procurement_module(self):
        """创建采购模块"""
        procurement_widget = QWidget()
        procurement_layout = QVBoxLayout()
        
        # 模块标题
        title = QLabel("采购清单管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; padding: 10px;")
        procurement_layout.addWidget(title)
        
        # 创建水平布局来放置选择区域和清单区域
        main_horizontal_layout = QHBoxLayout()
        
        # 左侧：系统选择区域
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_panel.setMinimumWidth(400)
        left_panel.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px;")
        left_layout = QVBoxLayout()
        
        # 系统选择标题
        system_title = QLabel("系统选择")
        system_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
        left_layout.addWidget(system_title)
        
        # 系统树形控件
        self.system_tree = QTreeWidget()
        self.system_tree.setHeaderLabel("锅炉系统")
        self.system_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        self.system_tree.itemClicked.connect(self.on_system_selected)
        left_layout.addWidget(self.system_tree)
        
        # 部件选择标题
        parts_title = QLabel("部件选择")
        parts_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px; margin-top: 10px;")
        left_layout.addWidget(parts_title)
        
        # 部件列表
        self.parts_list = QListWidget()
        self.parts_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        self.parts_list.itemDoubleClicked.connect(self.add_to_procurement_list)
        self.parts_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parts_list.customContextMenuRequested.connect(self.show_parts_context_menu)
        left_layout.addWidget(self.parts_list)
        
        # 添加提示信息
        info_label = QLabel("双击部件可添加到采购清单")
        info_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px; font-style: italic;")
        left_layout.addWidget(info_label)
        
        left_panel.setLayout(left_layout)
        main_horizontal_layout.addWidget(left_panel)
        
        # 右侧：采购清单区域
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # 采购清单标题
        list_title = QLabel("采购清单")
        list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
        right_layout.addWidget(list_title)
        
        # 采购清单表格
        self.procurement_table = QTableWidget()
        self.procurement_table.setColumnCount(6)
        self.procurement_table.setHorizontalHeaderLabels(["系统", "部件", "供应商", "单价", "数量", "小计"])
        self.procurement_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        self.procurement_table.horizontalHeader().setStretchLastSection(True)
        self.procurement_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.procurement_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.procurement_table.itemChanged.connect(self.update_total_price)
        right_layout.addWidget(self.procurement_table)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        
        # 删除选中项按钮
        self.delete_item_btn = QPushButton("删除选中项")
        self.delete_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.delete_item_btn.clicked.connect(self.delete_procurement_item)
        button_layout.addWidget(self.delete_item_btn)
        
        # 清空清单按钮
        self.clear_list_btn = QPushButton("清空清单")
        self.clear_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.clear_list_btn.clicked.connect(self.clear_procurement_list)
        button_layout.addWidget(self.clear_list_btn)
        
        button_layout.addStretch()
        
        # 总价格显示
        self.total_price_label = QLabel("总价格: ¥0.00")
        self.total_price_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #28a745;
            padding: 10px;
            background-color: #f8f9fa;
            border: 2px solid #28a745;
            border-radius: 8px;
        """)
        self.total_price_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(self.total_price_label)
        
        right_layout.addLayout(button_layout)
        
        # 导出按钮
        self.export_btn = QPushButton("导出采购清单")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.export_btn.clicked.connect(self.export_procurement_list)
        right_layout.addWidget(self.export_btn)
        
        right_panel.setLayout(right_layout)
        main_horizontal_layout.addWidget(right_panel)
        
        procurement_layout.addLayout(main_horizontal_layout)
        
        # 初始化系统树
        self.init_procurement_system_tree()
        
        procurement_widget.setLayout(procurement_layout)
        self.work_area.addWidget(procurement_widget)

    def init_procurement_system_tree(self):
        """初始化采购模块的系统树"""
        self.system_tree.clear()
        self.build_procurement_tree(self.system_data["categories"], self.system_tree)

    def build_procurement_tree(self, data, parent_item):
        """递归构建采购模块的树形结构"""
        for name, info in data.items():
            if isinstance(info, dict) and "children" in info:
                # 这是一个分类节点
                item = QTreeWidgetItem(parent_item, [name])
                item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
                self.build_procurement_tree(info["children"], item)
            else:
                # 这是一个叶子节点（具体项目）
                item = QTreeWidgetItem(parent_item, [name])
                item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))

    def on_system_selected(self, item):
        """当系统被选中时，加载对应的部件列表"""
        self.parts_list.clear()
        
        # 获取选中项的路径
        path = []
        current_item = item
        while current_item is not None:
            path.insert(0, current_item.text(0))
            current_item = current_item.parent()
        
        # 获取对应的数据
        data = self.get_data_by_path(path)
        if data and isinstance(data, dict):
            # 如果是叶子节点（具体项目），显示其部件
            if "parts" in data:
                for part in data["parts"]:
                    if isinstance(part, dict) and "name" in part:
                        part_name = part["name"]
                        part_description = part.get("description", "")
                        display_text = f"{part_name}"
                        if part_description:
                            display_text += f" - {part_description}"
                        
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.UserRole, part)
                        item.setData(Qt.UserRole + 1, path)  # 保存父级路径
                        
                        # 添加价格信息到工具提示
                        pricing_info = self.get_pricing_info_for_part_with_path(part, path)
                        if pricing_info and "suppliers" in pricing_info and pricing_info["suppliers"]:
                            supplier = pricing_info["suppliers"][0]
                            price = supplier.get("price", 0.0)
                            supplier_name = supplier.get("name", "未指定")
                            item.setToolTip(f"供应商: {supplier_name}\n价格: ¥{price:.2f}")
                        else:
                            item.setToolTip("暂无价格信息")
                        
                        self.parts_list.addItem(item)
            # 如果是分类节点，显示其子项目
            elif "children" in data:
                for child_name, child_data in data["children"].items():
                    if isinstance(child_data, dict) and "parts" in child_data:
                        for part in child_data["parts"]:
                            if isinstance(part, dict) and "name" in part:
                                part_name = part["name"]
                                part_description = part.get("description", "")
                                display_text = f"{child_name} - {part_name}"
                                if part_description:
                                    display_text += f" - {part_description}"
                                
                                item = QListWidgetItem(display_text)
                                item.setData(Qt.UserRole, part)
                                item.setData(Qt.UserRole + 1, path + [child_name])  # 保存父级路径
                                
                                # 添加价格信息到工具提示
                                pricing_info = self.get_pricing_info_for_part_with_path(part, path + [child_name])
                                if pricing_info and "suppliers" in pricing_info and pricing_info["suppliers"]:
                                    supplier = pricing_info["suppliers"][0]
                                    price = supplier.get("price", 0.0)
                                    supplier_name = supplier.get("name", "未指定")
                                    item.setToolTip(f"供应商: {supplier_name}\n价格: ¥{price:.2f}")
                                else:
                                    item.setToolTip("暂无价格信息")
                                
                                self.parts_list.addItem(item)

    def add_to_procurement_list(self, item):
        """将选中的部件添加到采购清单"""
        part_data = item.data(Qt.UserRole)
        parent_path = item.data(Qt.UserRole + 1)
        
        if not part_data:
            return
        
        # 获取当前行数
        current_row = self.procurement_table.rowCount()
        self.procurement_table.insertRow(current_row)
        
        # 设置部件信息
        part_name = part_data.get("name", "")
        part_description = part_data.get("description", "")
        display_name = f"{part_name} - {part_description}" if part_description else part_name
        
        # 获取系统名称
        system_name = "锅炉系统"
        if parent_path and len(parent_path) > 0:
            system_name = " - ".join(parent_path)
        
        # 获取价格信息（从父级数据中获取）
        pricing_info = self.get_pricing_info_for_part_with_path(part_data, parent_path)
        supplier_name = "未指定"
        unit_price = 0.0
        
        if pricing_info and "suppliers" in pricing_info and pricing_info["suppliers"]:
            # 使用第一个供应商的信息
            supplier = pricing_info["suppliers"][0]
            supplier_name = supplier.get("name", "未指定")
            unit_price = supplier.get("price", 0.0)
        
        # 填充表格
        self.procurement_table.setItem(current_row, 0, QTableWidgetItem(system_name))  # 系统名称
        self.procurement_table.setItem(current_row, 1, QTableWidgetItem(display_name))  # 部件名称
        self.procurement_table.setItem(current_row, 2, QTableWidgetItem(supplier_name))  # 供应商
        self.procurement_table.setItem(current_row, 3, QTableWidgetItem(f"¥{unit_price:.2f}"))  # 单价
        self.procurement_table.setItem(current_row, 4, QTableWidgetItem("1"))  # 数量
        self.procurement_table.setItem(current_row, 5, QTableWidgetItem(f"¥{unit_price:.2f}"))  # 小计
        
        # 更新总价格
        self.update_total_price()

    def get_pricing_info_for_part(self, part_data):
        """获取部件的价格信息"""
        # 遍历系统数据，查找包含该部件的项目
        def search_pricing_in_data(data, path=[]):
            for name, info in data.items():
                if isinstance(info, dict):
                    if "children" in info:
                        # 递归搜索子项目
                        result = search_pricing_in_data(info["children"], path + [name])
                        if result:
                            return result
                    elif "parts" in info:
                        # 检查这个项目是否包含目标部件
                        for part in info["parts"]:
                            if isinstance(part, dict) and part.get("name") == part_data.get("name"):
                                # 找到匹配的部件，返回价格信息
                                return info.get("pricing", {})
            return None
        
        return search_pricing_in_data(self.system_data["categories"])

    def get_pricing_info_for_part_with_path(self, part_data, parent_path):
        """根据父级路径获取部件的价格信息"""
        if not parent_path:
            return self.get_pricing_info_for_part(part_data)
        
        # 根据路径获取数据
        data = self.get_data_by_path(parent_path)
        if data and isinstance(data, dict) and "pricing" in data:
            return data.get("pricing", {})
        
        return None

    def delete_procurement_item(self):
        """删除采购清单中的选中项"""
        current_row = self.procurement_table.currentRow()
        if current_row >= 0:
            self.procurement_table.removeRow(current_row)
            self.update_total_price()

    def clear_procurement_list(self):
        """清空采购清单"""
        reply = QMessageBox.question(self, "确认清空", "确定要清空整个采购清单吗？", 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.procurement_table.setRowCount(0)
            self.update_total_price()

    def update_total_price(self):
        """更新总价格显示"""
        total = 0.0
        for row in range(self.procurement_table.rowCount()):
            unit_price_item = self.procurement_table.item(row, 3)
            quantity_item = self.procurement_table.item(row, 4)
            subtotal_item = self.procurement_table.item(row, 5)
            
            if unit_price_item and quantity_item:
                try:
                    # 提取单价和数量
                    unit_price_text = unit_price_item.text().replace("¥", "").strip()
                    quantity_text = quantity_item.text().strip()
                    
                    unit_price = float(unit_price_text)
                    quantity = float(quantity_text)
                    
                    # 计算小计
                    subtotal = unit_price * quantity
                    
                    # 更新小计显示
                    if subtotal_item:
                        subtotal_item.setText(f"¥{subtotal:.2f}")
                    
                    total += subtotal
                except ValueError:
                    pass
        
        self.total_price_label.setText(f"总价格: ¥{total:.2f}")

    def export_procurement_list(self):
        """导出采购清单"""
        if self.procurement_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "采购清单为空，无法导出！")
            return
        
        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"采购清单_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("采购清单\n")
                f.write("=" * 50 + "\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 写入表头
                f.write(f"{'系统':<15} {'部件':<30} {'供应商':<20} {'单价':<10} {'数量':<8} {'小计':<12}\n")
                f.write("-" * 100 + "\n")
                
                # 写入数据
                total = 0.0
                for row in range(self.procurement_table.rowCount()):
                    system = self.procurement_table.item(row, 0).text() if self.procurement_table.item(row, 0) else ""
                    part = self.procurement_table.item(row, 1).text() if self.procurement_table.item(row, 1) else ""
                    supplier = self.procurement_table.item(row, 2).text() if self.procurement_table.item(row, 2) else ""
                    unit_price = self.procurement_table.item(row, 3).text() if self.procurement_table.item(row, 3) else ""
                    quantity = self.procurement_table.item(row, 4).text() if self.procurement_table.item(row, 4) else ""
                    subtotal = self.procurement_table.item(row, 5).text() if self.procurement_table.item(row, 5) else ""
                    
                    f.write(f"{system:<15} {part:<30} {supplier:<20} {unit_price:<10} {quantity:<8} {subtotal:<12}\n")
                    
                    # 计算总价
                    try:
                        subtotal_value = float(subtotal.replace("¥", "").strip())
                        total += subtotal_value
                    except ValueError:
                        pass
                
                f.write("-" * 100 + "\n")
                f.write(f"{'总计':<75} ¥{total:.2f}\n")
            
            QMessageBox.information(self, "导出成功", f"采购清单已导出到: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出采购清单时发生错误: {str(e)}")

    def show_parts_context_menu(self, position):
        """显示部件列表的右键菜单"""
        item = self.parts_list.itemAt(position)
        if item:
            menu = QMenu()
            add_action = menu.addAction("添加到采购清单")
            action = menu.exec_(self.parts_list.mapToGlobal(position))
            if action == add_action:
                self.add_to_procurement_list(item)

    def init_tree(self):
        """初始化树形结构"""
        self.tree.clear()
        self.build_tree(self.system_data["categories"], self.tree)

    def build_tree(self, data, parent_item):
        """递归构建树形结构"""
        for name, info in data.items():
            if isinstance(info, dict) and "children" in info:
                # 这是一个分类节点
                item = QTreeWidgetItem(parent_item, [name])
                item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
                self.build_tree(info["children"], item)
            else:
                # 这是一个叶子节点（具体项目）
                item = QTreeWidgetItem(parent_item, [name])
                item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))

    def add_category(self):
        """添加分类"""
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个父分类！")
            return
            
        name, ok = QInputDialog.getText(self, "添加分类", "请输入分类名称:")
        if ok and name:
            # 在数据结构中添加新分类
            parent_path = self.get_item_path(current_item)
            self.add_category_to_data(parent_path, name)
            
            # 记住当前展开状态
            expanded_items = self.get_expanded_items()
            
            # 重新构建树
            self.init_tree()
            
            # 恢复展开状态
            self.restore_expanded_items(expanded_items)
            
            # 展开新添加的分类
            self.expand_new_item(parent_path + [name])
            
            self.save_data()

    def add_item(self):
        """添加具体项目"""
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个父分类！")
            return
            
        name, ok = QInputDialog.getText(self, "添加设备", "请输入设备名称:")
        if ok and name:
            # 在数据结构中添加新项目
            parent_path = self.get_item_path(current_item)
            self.add_item_to_data(parent_path, name)
            
            # 记住当前展开状态
            expanded_items = self.get_expanded_items()
            
            # 重新构建树
            self.init_tree()
            
            # 恢复展开状态
            self.restore_expanded_items(expanded_items)
            
            self.save_data()

    def delete_category(self):
        """删除分类或项目"""
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的项目！")
            return
        
        self.delete_category_from_context(current_item)

    def rename_category(self):
        """重命名分类或项目"""
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要重命名的项目！")
            return
            
        old_name = current_item.text(0)
        new_name, ok = QInputDialog.getText(self, "重命名", "请输入新名称:", text=old_name)
        if ok and new_name and new_name != old_name:
            try:
                parent_path = self.get_item_path(current_item.parent())
                if parent_path:
                    # 使用 get_parent_data_by_path 获取父级的 children 字典
                    parent_data = self.get_parent_data_by_path(parent_path + [old_name])
                    if parent_data and old_name in parent_data:
                        parent_data[new_name] = parent_data.pop(old_name)
                else:
                    if old_name in self.system_data["categories"]:
                        self.system_data["categories"][new_name] = self.system_data["categories"].pop(old_name)
                
                # 记住当前展开状态
                expanded_items = self.get_expanded_items()
                
                # 重新构建树
                self.init_tree()
                
                # 恢复展开状态
                self.restore_expanded_items(expanded_items)
                
                self.save_data()
                QMessageBox.information(self, "成功", f"'{old_name}' 已重命名为 '{new_name}'！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重命名失败: {str(e)}")

    def get_item_path(self, item):
        """获取项目在数据中的路径"""
        try:
            if not item:
                return None
            path = [item.text(0)]
            parent = item.parent()
            while parent:
                path.insert(0, parent.text(0))
                parent = parent.parent()
            return path
        except Exception as e:
            print(f"获取项目路径失败: {str(e)}")
            return None

    def get_data_by_path(self, path):
        """根据路径获取数据"""
        try:
            if not path:
                return self.system_data["categories"]
            current = self.system_data["categories"]
            for i, name in enumerate(path):
                if name in current:
                    if i == len(path) - 1:
                        # 这是最后一个元素，返回当前节点
                        return current[name]
                    elif "children" in current[name]:
                        # 还有更多路径，继续遍历
                        current = current[name]["children"]
                    else:
                        return None
                else:
                    return None
            return current
        except Exception as e:
            print(f"获取路径数据失败: {str(e)}, 路径: {path}")
            return None

    def get_current_item_data(self):
        """获取当前选中项目的数据"""
        try:
            if not self.current_item:
                return None
            
            path = self.get_item_path(self.current_item)
            if not path:
                return None
            
            data = self.get_data_by_path(path)
            if not data or "children" in data:
                return None
            
            return data
        except Exception as e:
            print(f"获取当前项目数据失败: {e}")
            return None

    def get_parent_data_by_path(self, path):
        """根据路径获取父级数据"""
        if not path:
            return self.system_data["categories"]
        current = self.system_data["categories"]
        for i, name in enumerate(path[:-1]):  # 除了最后一个元素
            if name in current and "children" in current[name]:
                current = current[name]["children"]
            else:
                return None
        return current

    def add_category_to_data(self, parent_path, name):
        """在数据中添加分类"""
        if parent_path:
            # 检查当前路径指向的是否是一个分类（有children属性）
            current_data = self.get_data_by_path(parent_path)
            if current_data and isinstance(current_data, dict) and "children" in current_data:
                # 当前路径指向的是一个分类，直接在其children中添加
                current_data["children"][name] = {"children": {}}
            else:
                # 当前路径指向的是一个项目，需要获取其父级
                parent_data = self.get_parent_data_by_path(parent_path)
                if parent_data:
                    parent_data[name] = {"children": {}}
                else:
                    # 如果还是找不到父级，可能是根目录的情况
                    # 检查是否在根目录下添加
                    if len(parent_path) == 1 and parent_path[0] in self.system_data["categories"]:
                        # 在根分类下添加
                        self.system_data["categories"][parent_path[0]]["children"][name] = {"children": {}}
        else:
            self.system_data["categories"][name] = {"children": {}}
            
    def add_item_to_data(self, parent_path, name):
        """在数据中添加具体项目"""
        if parent_path:
            # 检查当前路径指向的是否是一个分类（有children属性）
            current_data = self.get_data_by_path(parent_path)
            if current_data and isinstance(current_data, dict) and "children" in current_data:
                # 当前路径指向的是一个分类，直接在其children中添加
                current_data["children"][name] = {
                    "content": "",
                    "tags": [],
                    "images": [],
                    "technical_params": {},
                    "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                    "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                    "parts": []
                }
            else:
                # 当前路径指向的是一个项目，需要获取其父级
                parent_data = self.get_parent_data_by_path(parent_path)
                if parent_data:
                    parent_data[name] = {
                        "content": "",
                        "tags": [],
                        "images": [],
                        "technical_params": {},
                        "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                        "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                        "parts": []
                    }
                else:
                    # 如果还是找不到父级，可能是根目录的情况
                    # 检查是否在根目录下添加
                    if len(parent_path) == 1 and parent_path[0] in self.system_data["categories"]:
                        # 在根分类下添加
                        self.system_data["categories"][parent_path[0]]["children"][name] = {
                            "content": "",
                            "tags": [],
                            "images": [],
                            "technical_params": {},
                            "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                            "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                            "parts": []
                        }
        else:
            self.system_data["categories"][name] = {
                "content": "",
                "tags": [],
                "images": [],
                "technical_params": {},
                "pricing": {"base_price": 0, "currency": "CNY", "suppliers": []},
                "maintenance": {"cycle": "", "procedures": "", "notes": ""},
                "parts": []
            }

    def get_expanded_items(self):
        """获取当前展开的项目"""
        expanded = []
        self.collect_expanded_items(self.tree.invisibleRootItem(), [], expanded)
        return expanded

    def collect_expanded_items(self, item, path, expanded):
        """收集展开的项目路径"""
        for i in range(item.childCount()):
            child = item.child(i)
            child_path = path + [child.text(0)]
            if child.isExpanded():
                expanded.append(child_path)
            self.collect_expanded_items(child, child_path, expanded)

    def restore_expanded_items(self, expanded_items):
        """恢复展开状态"""
        for path in expanded_items:
            self.expand_path(path)

    def expand_path(self, path):
        """展开指定路径"""
        current = self.tree.invisibleRootItem()
        for name in path:
            found = False
            for i in range(current.childCount()):
                child = current.child(i)
                if child.text(0) == name:
                    child.setExpanded(True)
                    current = child
                    found = True
                    break
            if not found:
                break

    def expand_new_item(self, path):
        """展开新添加的项目"""
        self.expand_path(path)

    def load_content(self, item):
        """加载内容"""
        try:
            print("=== 开始加载内容 ===")
            # 设置加载标志，防止自动保存触发
            self._initializing = True
            
            if not item:
                print("没有选中项目，跳过加载")
                self._initializing = False
                return
                
            path = self.get_item_path(item)
            print(f"项目路径: {path}")
            if not path:
                print("无法获取项目路径，跳过加载")
                return
                
            # 检查是否是叶子节点（具体项目）
            data = self.get_data_by_path(path)
            if not data:
                print("无法找到数据，清空所有内容")
                # 无法找到数据，清空内容
                self.content_edit.clear()
                self.tags_edit.clear()
                self.tech_table.setRowCount(0)
                self.base_price_edit.clear()
                self.supplier_table.setRowCount(0)
                self.cycle_edit.clear()
                self.procedures_edit.clear()
                self.notes_edit.clear()
                self.load_images([])
                self.load_principle_images([])
                try:
                    if hasattr(self, 'supplier_image_management_section'):
                        self.supplier_image_management_section.hide()
                    if hasattr(self, 'current_supplier_info'):
                        self.current_supplier_info.setText("请双击供应商表格中的供应商来管理其产品图片")
                except Exception as e:
                    print(f"隱藏供應商圖片管理區域失敗: {str(e)}")
                    pass
                return
                
            if "children" in data:
                print(f"这是分类节点: {item.text(0)}，清空所有内容")
                # 这是一个分类节点，清空内容
                self.content_edit.clear()
                self.tags_edit.clear()
                self.tech_table.setRowCount(0)
                self.base_price_edit.clear()
                self.supplier_table.setRowCount(0)
                self.cycle_edit.clear()
                self.procedures_edit.clear()
                self.notes_edit.clear()
                self.load_images([])
                self.load_principle_images([])
                try:
                    if hasattr(self, 'supplier_image_management_section'):
                        self.supplier_image_management_section.hide()
                    if hasattr(self, 'current_supplier_info'):
                        self.current_supplier_info.setText("请双击供应商表格中的供应商来管理其产品图片")
                except Exception as e:
                    print(f"隱藏供應商圖片管理區域失敗: {str(e)}")
                    pass
                return
                
            # 这是一个叶子节点，加载详细信息
            print(f"这是叶子节点: {item.text(0)}，开始加载详细信息")
            self.current_item = item
            
            # 加载基本信息
            print("加载基本信息...")
            self.content_edit.setPlainText(data.get("content", ""))
            self.tags_edit.setText(", ".join(data.get("tags", [])))
            
            # 加载技术参数
            print("加载技术参数...")
            self.load_tech_params(data.get("technical_params", {}))
            
            # 加载价格信息
            print("加载价格信息...")
            pricing_data = data.get("pricing", {})
            print(f"价格数据: {pricing_data}")
            self.load_pricing(pricing_data)
            
            # 加载维护信息
            print("加载维护信息...")
            self.load_maintenance(data.get("maintenance", {}))
            
            # 加载图片
            print("加载图片...")
            self.load_images(data.get("images", []))
            
            # 加载原理图片
            print("加载原理图片...")
            self.load_principle_images(data.get("principle_images", []))
            
            # 加载零部件列表
            print("加载零部件列表...")
            self.load_parts_list(data)
            
            # 隐藏供应商图片管理区域
            try:
                if hasattr(self, 'supplier_image_management_section'):
                    self.supplier_image_management_section.hide()
                if hasattr(self, 'current_supplier_info'):
                    self.current_supplier_info.setText("请双击供应商表格中的供应商来管理其产品图片")
            except Exception as e:
                print(f"隱藏供應商圖片管理區域失敗: {str(e)}")
                pass
            
            print("=== 内容加载完成 ===")
            
            # 清除加载标志，恢复自动保存
            self._initializing = False
        except Exception as e:
            error_msg = f"加载内容失败: {str(e)}"
            print(error_msg)
            # 确保在异常情况下也清除加载标志
            self._initializing = False
            QMessageBox.critical(self, "加载失败", error_msg)

    def load_tech_params(self, params):
        """加载技术参数"""
        self.tech_table.setRowCount(0)
        for param_name, param_value in params.items():
            row = self.tech_table.rowCount()
            self.tech_table.insertRow(row)
            self.tech_table.setItem(row, 0, QTableWidgetItem(param_name))
            self.tech_table.setItem(row, 1, QTableWidgetItem(str(param_value)))

    def load_pricing(self, pricing):
        """加载价格信息"""
        print(f"开始加载价格信息: {pricing}")
        
        # 临时禁用自动保存，防止UI变化触发自动保存
        auto_save_enabled = not (hasattr(self, '_initializing') and self._initializing)
        if auto_save_enabled:
            self._initializing = True
        
        # 確保清空所有現有數據
        self.base_price_edit.clear()
        self.supplier_table.setRowCount(0)
        
        # 設置基礎價格
        self.base_price_edit.setText(str(pricing.get("base_price", 0)))
        
        # 設置貨幣
        currency = pricing.get("currency", "CNY")
        index = self.currency_combo.findText(currency)
        if index >= 0:
            self.currency_combo.setCurrentIndex(index)
        
        # 加載供應商信息
        suppliers = pricing.get("suppliers", [])
        print(f"加載 {len(suppliers)} 個供應商")
        
        # 確保供應商表格完全清空
        self.supplier_table.clearContents()
        self.supplier_table.setRowCount(0)
        
        for supplier in suppliers:
            row = self.supplier_table.rowCount()
            self.supplier_table.insertRow(row)
            # 型号列（第0列）
            self.supplier_table.setItem(row, 0, QTableWidgetItem(""))  # 型号暂时为空
            # 供应商列（第1列）
            self.supplier_table.setItem(row, 1, QTableWidgetItem(supplier.get("name", "")))
            # 价格列（第2列）
            self.supplier_table.setItem(row, 2, QTableWidgetItem(str(supplier.get("price", 0))))
            # 供货周期列（第3列）
            self.supplier_table.setItem(row, 3, QTableWidgetItem(supplier.get("lead_time", "")))
            # 联系方式列（第4列）
            self.supplier_table.setItem(row, 4, QTableWidgetItem(supplier.get("contact", "")))
            
            # 顯示供應商圖片信息（第5列）
            supplier_images = supplier.get("images", [])
            if supplier_images:
                image_count = len(supplier_images)
                self.supplier_table.setItem(row, 5, QTableWidgetItem(f"📷 {image_count}张图片"))
                print(f"供應商 '{supplier.get('name', '')}' 有 {image_count} 張圖片")
            else:
                self.supplier_table.setItem(row, 5, QTableWidgetItem("无图片"))
                print(f"供應商 '{supplier.get('name', '')}' 無圖片")
        
        print(f"價格信息加載完成，共 {self.supplier_table.rowCount()} 行供應商")
        
        # 強制刷新表格
        self.supplier_table.viewport().update()
        
        # 如果之前启用了自动保存，现在恢复
        if auto_save_enabled:
            self._initializing = False

    def load_maintenance(self, maintenance):
        """加载维护信息"""
        self.cycle_edit.setText(maintenance.get("cycle", ""))
        self.procedures_edit.setPlainText(maintenance.get("procedures", ""))
        self.notes_edit.setPlainText(maintenance.get("notes", ""))

    def load_images(self, images):
        """加载图片缩略图"""
        try:
            print(f"開始載入圖片縮略圖，圖片數量: {len(images) if images else 0}")
            
            # 清除所有布局项，但保留占位符标签
            while self.images_layout.count() > 0:
                item = self.images_layout.takeAt(0)
                if item.widget():
                    # 不要删除占位符标签，只删除缩略图小部件
                    if item.widget() != self.image_thumbnail_label:
                        item.widget().deleteLater()
            
            if images and len(images) > 0:
                # 隐藏提示标签
                self.image_thumbnail_label.hide()
                print(f"隱藏提示標籤，開始載入 {len(images)} 張圖片")
                
                # 验证图片文件并过滤掉不存在的文件
                valid_images = []
                missing_images = []
                
                for image_filename in images:
                    image_path = os.path.join(self.images_dir, image_filename)
                    if os.path.exists(image_path):
                        valid_images.append(image_filename)
                    else:
                        missing_images.append(image_filename)
                        print(f"警告: 图片文件不存在: {image_path}")
                
                if missing_images:
                    print(f"發現 {len(missing_images)} 個缺失的圖片文件: {missing_images}")
                    # 可以选择是否显示警告给用户
                    if len(missing_images) > 0:
                        QMessageBox.warning(self, "圖片文件缺失", 
                                          f"發現 {len(missing_images)} 個圖片文件缺失:\n" + 
                                          "\n".join(missing_images[:5]) + 
                                          ("\n..." if len(missing_images) > 5 else ""))
                
                # 为每张有效图片创建缩略图
                for i, image_filename in enumerate(valid_images):
                    try:
                        image_path = os.path.join(self.images_dir, image_filename)
                        print(f"處理第 {i+1} 張圖片: {image_filename}")
                        print(f"完整路徑: {image_path}")
                        
                        # 验证文件是否可读
                        if not os.access(image_path, os.R_OK):
                            print(f"警告: 图片文件无读取权限: {image_path}")
                            continue
                        
                        # 验证文件大小
                        file_size = os.path.getsize(image_path)
                        if file_size == 0:
                            print(f"警告: 图片文件为空: {image_path}")
                            continue
                        
                        print(f"圖片文件存在且可讀，大小: {file_size} 字節")
                        # 创建完整的图片路径列表用于导航
                        full_image_paths = [os.path.join(self.images_dir, img) for img in valid_images]
                        thumbnail_widget = ImageThumbnailWidget(image_path, full_image_paths, i, self.images_widget, self.delete_image_callback)
                        self.images_layout.addWidget(thumbnail_widget)
                        print(f"縮略圖已添加到佈局")
                    except Exception as e:
                        print(f"創建第 {i+1} 張圖片縮略圖失敗: {str(e)}")
                        continue
                
                # 添加弹性空间
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.images_layout.addItem(spacer)
                print("已添加彈性空間")
                
                if len(valid_images) == 0:
                    # 如果没有有效图片，显示提示
                    self.image_thumbnail_label.show()
                    self.image_thumbnail_label.setText("所有圖片文件均缺失")
            else:
                # 显示提示标签
                self.image_thumbnail_label.show()
                self.image_thumbnail_label.setText("暂无图片，点击下方按钮添加图片")
                print("顯示提示標籤：暫無圖片")
                
                # 添加弹性空间
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.images_layout.addItem(spacer)
                print("已添加彈性空間")
            
            print("圖片縮略圖載入完成")
            
        except Exception as e:
            error_msg = f"載入圖片縮略圖失敗: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "錯誤", error_msg)

    def load_principle_images(self, images):
        """加载原理图片缩略图"""
        try:
            print(f"開始載入原理圖片縮略圖，圖片數量: {len(images) if images else 0}")
            
            # 清除所有布局项，但保留占位符标签
            while self.principle_images_layout.count() > 0:
                item = self.principle_images_layout.takeAt(0)
                if item.widget():
                    # 不要删除占位符标签，只删除缩略图小部件
                    if item.widget() != self.principle_image_thumbnail_label:
                        item.widget().deleteLater()
            
            if images and len(images) > 0:
                # 隐藏提示标签
                self.principle_image_thumbnail_label.hide()
                print(f"隱藏原理圖片提示標籤，開始載入 {len(images)} 張原理圖片")
                
                # 验证图片文件并过滤掉不存在的文件
                valid_images = []
                missing_images = []
                
                for image_filename in images:
                    image_path = os.path.join(self.images_dir, image_filename)
                    if os.path.exists(image_path):
                        valid_images.append(image_filename)
                    else:
                        missing_images.append(image_filename)
                        print(f"警告: 原理图片文件不存在: {image_path}")
                
                if missing_images:
                    print(f"發現 {len(missing_images)} 個缺失的原理圖片文件: {missing_images}")
                
                # 为每张有效图片创建缩略图
                for i, image_filename in enumerate(valid_images):
                    try:
                        image_path = os.path.join(self.images_dir, image_filename)
                        print(f"處理第 {i+1} 張原理圖片: {image_filename}")
                        print(f"完整路徑: {image_path}")
                        
                        # 验证文件是否可读
                        if not os.access(image_path, os.R_OK):
                            print(f"警告: 原理图片文件无读取权限: {image_path}")
                            continue
                        
                        # 验证文件大小
                        file_size = os.path.getsize(image_path)
                        if file_size == 0:
                            print(f"警告: 原理图片文件为空: {image_path}")
                            continue
                        
                        print(f"原理圖片文件存在且可讀，大小: {file_size} 字節")
                        # 创建完整的图片路径列表用于导航
                        full_image_paths = [os.path.join(self.images_dir, img) for img in valid_images]
                        thumbnail_widget = ImageThumbnailWidget(image_path, full_image_paths, i, self.principle_images_widget, self.delete_principle_image_callback)
                        self.principle_images_layout.addWidget(thumbnail_widget)
                        print(f"原理圖片縮略圖已添加到佈局")
                    except Exception as e:
                        print(f"創建第 {i+1} 張原理圖片縮略圖失敗: {str(e)}")
                        continue
                
                # 添加弹性空间
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.principle_images_layout.addItem(spacer)
                print("已添加原理圖片彈性空間")
                
                if len(valid_images) == 0:
                    # 如果没有有效图片，显示提示
                    self.principle_image_thumbnail_label.show()
                    self.principle_image_thumbnail_label.setText("所有原理圖片文件均缺失")
            else:
                # 显示提示标签
                self.principle_image_thumbnail_label.show()
                self.principle_image_thumbnail_label.setText("暂无原理图片，点击下方按钮添加图片")
                print("顯示原理圖片提示標籤：暫無原理圖片")
                
                # 添加弹性空间
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.principle_images_layout.addItem(spacer)
                print("已添加原理圖片彈性空間")
            
            print("原理圖片縮略圖載入完成")
            
        except Exception as e:
            error_msg = f"載入原理圖片縮略圖失敗: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "錯誤", error_msg)

    def load_supplier_images(self, images):
        """加载供应商图片缩略图"""
        try:
            print(f"開始載入供應商圖片縮略圖，圖片數量: {len(images) if images else 0}")
            
            # 清除現有的縮略圖，但保留占位符标签
            while self.supplier_image_thumbnail_layout.count() > 0:
                item = self.supplier_image_thumbnail_layout.takeAt(0)
                if item.widget():
                    # 不要删除占位符标签，只删除缩略图小部件
                    if item.widget() != self.supplier_image_thumbnail_label:
                        item.widget().deleteLater()
            
            if images and len(images) > 0:
                # 隱藏佔位符標籤
                self.supplier_image_thumbnail_label.hide()
                
                # 验证图片文件并过滤掉不存在的文件
                valid_images = []
                missing_images = []
                
                for image_filename in images:
                    image_path = os.path.join(self.images_dir, image_filename)
                    if os.path.exists(image_path):
                        valid_images.append(image_filename)
                    else:
                        missing_images.append(image_filename)
                        print(f"警告: 供應商圖片文件不存在: {image_path}")
                
                if missing_images:
                    print(f"發現 {len(missing_images)} 個缺失的供應商圖片文件: {missing_images}")
                
                # 添加縮略圖
                for i, image_name in enumerate(valid_images):
                    try:
                        print(f"正在載入供應商圖片 {i+1}: {image_name}")
                        image_path = os.path.join(self.images_dir, image_name)
                        
                        # 验证文件是否可读
                        if not os.access(image_path, os.R_OK):
                            print(f"警告: 供應商圖片文件无读取权限: {image_path}")
                            continue
                        
                        # 验证文件大小
                        file_size = os.path.getsize(image_path)
                        if file_size == 0:
                            print(f"警告: 供應商圖片文件为空: {image_path}")
                            continue
                        
                        print(f"供應商圖片文件存在且可讀，大小: {file_size} 字節")
                        # 创建完整的图片路径列表用于导航
                        full_image_paths = [os.path.join(self.images_dir, img) for img in valid_images]
                        thumbnail_widget = ImageThumbnailWidget(image_path, full_image_paths, i, self.supplier_image_thumbnail_container)
                        self.supplier_image_thumbnail_layout.addWidget(thumbnail_widget)
                        print(f"成功添加供應商圖片縮略圖: {image_name}")
                    except Exception as e:
                        print(f"創建第 {i+1} 張供應商圖片縮略圖失敗: {str(e)}")
                        continue
                
                # 添加彈性空間
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.supplier_image_thumbnail_layout.addItem(spacer)
                
                print(f"供應商圖片縮略圖載入完成，共 {len(valid_images)} 張")
                
                if len(valid_images) == 0:
                    # 如果没有有效图片，显示提示
                    self.supplier_image_thumbnail_label.show()
                    self.supplier_image_thumbnail_label.setText("所有供應商圖片文件均缺失")
            else:
                # 顯示佔位符標籤
                self.supplier_image_thumbnail_label.show()
                self.supplier_image_thumbnail_label.setText("暂无供应商图片，点击下方按钮添加图片")
                print("沒有供應商圖片，顯示佔位符")
                
                # 添加彈性空間
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.supplier_image_thumbnail_layout.addItem(spacer)
                
        except Exception as e:
            error_msg = f"載入供應商圖片縮略圖失敗: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "錯誤", error_msg)

    def verify_and_repair_image_references(self):
        """验证并修复图片引用"""
        try:
            print("開始驗證和修復圖片引用...")
            
            def check_and_repair_images_in_data(data, path=""):
                """递归检查数据中的图片引用"""
                repaired_count = 0
                
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, dict):
                        if "children" in value:
                            # 这是一个分类，递归检查子项
                            repaired_count += check_and_repair_images_in_data(value, current_path)
                        else:
                            # 这是一个项目，检查图片字段
                            for image_field in ["images", "principle_images", "supplier_images"]:
                                if image_field in value and isinstance(value[image_field], list):
                                    original_images = value[image_field].copy()
                                    valid_images = []
                                    
                                    for image_filename in original_images:
                                        image_path = os.path.join(self.images_dir, image_filename)
                                        if os.path.exists(image_path) and os.access(image_path, os.R_OK):
                                            file_size = os.path.getsize(image_path)
                                            if file_size > 0:
                                                valid_images.append(image_filename)
                                            else:
                                                print(f"發現空文件，將移除: {image_path}")
                                        else:
                                            print(f"發現無效圖片引用，將移除: {image_path}")
                                    
                                    if len(valid_images) != len(original_images):
                                        value[image_field] = valid_images
                                        repaired_count += len(original_images) - len(valid_images)
                                        print(f"修復 {current_path} 的 {image_field}: 移除了 {len(original_images) - len(valid_images)} 個無效引用")
                
                return repaired_count
            
            total_repaired = check_and_repair_images_in_data(self.system_data)
            
            if total_repaired > 0:
                # 保存修复后的数据
                self.save_data()
                QMessageBox.information(self, "圖片引用修復完成", 
                                      f"已修復 {total_repaired} 個無效的圖片引用。\n數據已自動保存。")
                print(f"圖片引用修復完成，共修復 {total_repaired} 個引用")
            else:
                QMessageBox.information(self, "圖片引用檢查完成", "所有圖片引用均有效。")
                print("圖片引用檢查完成，無需修復")
                
        except Exception as e:
            error_msg = f"驗證和修復圖片引用失敗: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "錯誤", error_msg)

    def save_content(self):
        """保存内容"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存内容！")
                return
                
            data["content"] = self.content.toPlainText()
            self.save_data()
            QMessageBox.information(self, "成功", "内容已保存！")
        except Exception as e:
            error_msg = f"保存内容失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "保存失败", error_msg)

    def save_tags(self):
        """保存标签"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存标签！")
                return
                
            tags_text = self.tags_input.text().strip()
            if tags_text:
                tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
                data["tags"] = tags
                self.update_tag_index()
                self.save_data()
                QMessageBox.information(self, "成功", "标签已保存！")
            else:
                data["tags"] = []
                self.update_tag_index()
                self.save_data()
                QMessageBox.information(self, "成功", "标签已清空！")
        except Exception as e:
            error_msg = f"保存标签失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "保存失败", error_msg)

    def update_tag_index(self):
        """更新标签索引"""
        self.system_data["tags"] = {}
        self.build_tag_index(self.system_data["categories"], [])

    def build_tag_index(self, data, path):
        """构建标签索引"""
        for name, info in data.items():
            current_path = path + [name]
            if isinstance(info, dict) and "children" in info:
                # 这是一个分类节点
                self.build_tag_index(info["children"], current_path)
            else:
                # 这是一个叶子节点
                tags = info.get("tags", [])
                for tag in tags:
                    if tag not in self.system_data["tags"]:
                        self.system_data["tags"][tag] = []
                    self.system_data["tags"][tag].append(current_path)

    def search_by_tag(self):
        """智能搜索功能"""
        query = self.search_input.text().strip().lower()
        if not query:
            self.search_results.clear()
            return
            
        results = []
        
        # 1. 搜索标签 - 支持模糊搜索
        for tag, paths in self.system_data["tags"].items():
            if query in tag.lower():  # 模糊匹配
                for path in paths:
                    results.append((path, f"标签: {tag}"))
        
        # 2. 搜索设备名称 - 支持模糊搜索
        self.search_by_name(self.system_data["categories"], [], query, results)
        
        # 3. 搜索设备内容 - 支持模糊搜索
        self.search_by_content(self.system_data["categories"], [], query, results)
        
        # 去重
        unique_results = []
        seen_paths = set()
        for path, match_type in results:
            path_str = ' > '.join(path)
            if path_str not in seen_paths:
                unique_results.append((path, match_type))
                seen_paths.add(path_str)
        
        # 显示结果
        self.search_results.clear()
        for path, match_type in unique_results:
            item_text = f"{' > '.join(path)} ({match_type})"
            self.search_results.addItem(item_text)
        
        # 显示搜索结果数量
        if unique_results:
            self.search_results.setToolTip(f"找到 {len(unique_results)} 个结果")
        else:
            self.search_results.setToolTip("未找到匹配结果")

    def search_by_name(self, data, current_path, query, results):
        """递归搜索设备名称 - 支持模糊搜索"""
        for name, info in data.items():
            path = current_path + [name]
            
            # 检查设备名称是否匹配 - 支持模糊搜索
            if query in name.lower():  # 模糊匹配
                results.append((path, f"名称: {name}"))
            
            # 递归搜索子分类
            if isinstance(info, dict) and "children" in info:
                self.search_by_name(info["children"], path, query, results)

    def search_by_content(self, data, current_path, query, results):
        """递归搜索设备内容和零部件 - 支持模糊搜索"""
        for name, info in data.items():
            path = current_path + [name]
            
            # 检查设备内容是否匹配
            if isinstance(info, dict) and "content" in info:
                content = info.get("content", "").lower()
                if query in content:  # 模糊匹配
                    results.append((path, f"内容: {name}"))
                
                # 搜索零部件
                if "parts" in info:
                    for part in info["parts"]:
                        part_name = part.get("name", "").lower()
                        part_description = part.get("description", "").lower()
                        
                        # 检查零部件名称和描述是否匹配
                        if query in part_name or query in part_description:
                            part_path = path + [f"[零部件] {part.get('name', '未命名')}"]
                            results.append((part_path, f"零部件: {part.get('name', '未命名')}"))
            
            # 递归搜索子分类
            if isinstance(info, dict) and "children" in info:
                self.search_by_content(info["children"], path, query, results)

    def select_search_result(self, item):
        """选择搜索结果"""
        item_text = item.text()
        # 提取路径部分 - 支持新的格式
        if " (标签:" in item_text:
            path_text = item_text.split(" (标签:")[0]
        elif " (名称:" in item_text:
            path_text = item_text.split(" (名称:")[0]
        elif " (内容:" in item_text:
            path_text = item_text.split(" (内容:")[0]
        elif " (零部件:" in item_text:
            path_text = item_text.split(" (零部件:")[0]
        else:
            path_text = item_text
        
        path = path_text.split(" > ")
        
        # 检查是否是零部件搜索结果
        if len(path) > 0 and path[-1].startswith("[零部件] "):
            # 这是零部件搜索结果，需要选择父设备并切换到零部件标签页
            parent_path = path[:-1]  # 移除零部件部分
            self.find_and_select_item(parent_path)
            
            # 切换到零部件标签页
            self.tab_widget.setCurrentIndex(4)  # 零部件附页是第5个标签页（索引4）
            
            # 查找并选择对应的零部件
            part_name = path[-1].replace("[零部件] ", "")
            self.select_part_by_name(part_name)
        else:
            # 在树中查找并选择
            self.find_and_select_item(path)

    def select_part_by_name(self, part_name):
        """根据名称选择零部件"""
        try:
            if not hasattr(self, 'parts_list') or not self.parts_list:
                return
            
            # 在零部件列表中查找匹配的零部件
            for i in range(self.parts_list.count()):
                item = self.parts_list.item(i)
                if item.text() == part_name:
                    # 选择这个零部件
                    self.parts_list.setCurrentRow(i)
                    self.parts_list.itemClicked.emit(item)
                    print(f"已选择零部件: {part_name}")
                    return
            
            print(f"未找到零部件: {part_name}")
            
        except Exception as e:
            print(f"选择零部件失败: {e}")

    def find_and_select_item(self, path):
        """在树中查找并选择项目"""
        current = self.tree.invisibleRootItem()
        for name in path:
            found = False
            for i in range(current.childCount()):
                child = current.child(i)
                if child.text(0) == name:
                    current = child
                    found = True
                    break
            if not found:
                return
        
        # 选择并展开到该项目
        self.tree.setCurrentItem(current)
        self.tree.scrollToItem(current)
        self.load_content(current)

    def add_tech_param(self):
        """添加技术参数"""
        row = self.tech_table.rowCount()
        self.tech_table.insertRow(row)
        self.tech_table.setItem(row, 0, QTableWidgetItem(""))
        self.tech_table.setItem(row, 1, QTableWidgetItem(""))

    def del_tech_param(self):
        """删除技术参数"""
        current_row = self.tech_table.currentRow()
        if current_row >= 0:
            self.tech_table.removeRow(current_row)

    def save_tech_params(self):
        """保存技术参数"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存技术参数！")
                return
                
            params = {}
            for row in range(self.tech_table.rowCount()):
                param_name = self.tech_table.item(row, 0)
                param_value = self.tech_table.item(row, 1)
                if param_name and param_value and param_name.text().strip():
                    params[param_name.text().strip()] = param_value.text().strip()
            
            data["technical_params"] = params
            self.save_data()
            QMessageBox.information(self, "成功", "技术参数已保存！")
        except Exception as e:
            error_msg = f"保存技术参数失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "保存失败", error_msg)

    def add_supplier(self):
        """添加供应商"""
        print("添加供应商按钮被点击")
        row = self.supplier_table.rowCount()
        self.supplier_table.insertRow(row)
        # 型号列（第0列）
        self.supplier_table.setItem(row, 0, QTableWidgetItem(""))
        # 供应商列（第1列）
        self.supplier_table.setItem(row, 1, QTableWidgetItem(""))
        # 价格列（第2列）
        self.supplier_table.setItem(row, 2, QTableWidgetItem(""))
        # 供货周期列（第3列）
        self.supplier_table.setItem(row, 3, QTableWidgetItem(""))
        # 联系方式列（第4列）
        self.supplier_table.setItem(row, 4, QTableWidgetItem(""))
        # 产品图片列（第5列）
        self.supplier_table.setItem(row, 5, QTableWidgetItem("无图片"))
        print(f"已添加第 {row} 行供应商")
        # 触发自动保存
        print("调用自动保存价格信息...")
        self.auto_save_pricing()
        print("自动保存价格信息调用完成")

    def del_supplier(self):
        """删除供应商"""
        print("删除供应商按钮被点击")
        current_row = self.supplier_table.currentRow()
        if current_row >= 0:
            print(f"删除第 {current_row} 行供应商")
            self.supplier_table.removeRow(current_row)
            # 触发自动保存
            print("调用自动保存价格信息...")
            self.auto_save_pricing()
            print("自动保存价格信息调用完成")
        else:
            print("没有选中的供应商行")

    def save_pricing(self):
        """保存价格信息"""
        try:
            print("=== 开始手动保存价格信息 ===")
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            path = self.get_item_path(self.current_item)
            print(f"当前设备路径: {path}")
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存价格信息！")
                return
                
            # 保存基础价格
            try:
                base_price = float(self.base_price_edit.text() or 0)
            except ValueError:
                base_price = 0
            
            pricing = {
                "base_price": base_price,
                "currency": self.currency_combo.currentText(),
                "suppliers": []
            }
            
            print(f"供应商表格行数: {self.supplier_table.rowCount()}")
            # 保存供应商信息
            for row in range(self.supplier_table.rowCount()):
                # 型号列（第0列）- 暂时不保存
                name_item = self.supplier_table.item(row, 1)  # 供应商名称在第1列
                price_item = self.supplier_table.item(row, 2)  # 价格在第2列
                lead_time_item = self.supplier_table.item(row, 3)  # 供货周期在第3列
                contact_item = self.supplier_table.item(row, 4)  # 联系方式在第4列
                
                print(f"第{row}行 - 供应商名称: {name_item.text() if name_item else 'None'}")
                
                if name_item and name_item.text().strip():
                    try:
                        price = float(price_item.text() if price_item else 0)
                    except ValueError:
                        price = 0
                    
                    supplier = {
                        "name": name_item.text().strip(),
                        "price": price,
                        "lead_time": lead_time_item.text() if lead_time_item else "",
                        "contact": contact_item.text() if contact_item else "",
                        "images": []  # 初始化供应商图片列表
                    }
                    
                    # 如果供应商已存在，保留其图片信息
                    existing_suppliers = data.get("pricing", {}).get("suppliers", [])
                    print(f"现有供应商数量: {len(existing_suppliers)}")
                    for existing_supplier in existing_suppliers:
                        if existing_supplier.get("name") == supplier["name"]:
                            supplier["images"] = existing_supplier.get("images", [])
                            print(f"保留供应商 '{supplier['name']}' 的 {len(supplier['images'])} 张图片")
                            break
                    
                    pricing["suppliers"].append(supplier)
                    print(f"添加供应商: {supplier['name']}")
            
            print(f"最终保存的供应商数量: {len(pricing['suppliers'])}")
            data["pricing"] = pricing
            self.save_data()
            print("=== 手动保存价格信息完成 ===")
            QMessageBox.information(self, "成功", f"供应商信息已保存！\n共保存 {len(pricing['suppliers'])} 个供应商。")
        except Exception as e:
            error_msg = f"保存价格信息失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "保存失败", error_msg)

    def save_maintenance(self):
        """保存维护信息"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存维护信息！")
                return
                
            maintenance = {
                "cycle": self.maintenance_cycle.text(),
                "procedures": self.maintenance_procedures.toPlainText(),
                "notes": self.maintenance_notes.toPlainText()
            }
            
            data["maintenance"] = maintenance
            self.save_data()
            QMessageBox.information(self, "成功", "维护信息已保存！")
        except Exception as e:
            error_msg = f"保存维护信息失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "保存失败", error_msg)

    def insert_image(self):
        """插入图片"""
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file_paths:
                self.current_image_paths = file_paths
                QMessageBox.information(self, "提示", f"已选择 {len(file_paths)} 张图片，请点击保存按钮保存图片！")
        except Exception as e:
            error_msg = f"插入图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def save_image(self):
        """保存图片"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            if not hasattr(self, 'current_image_paths') or not self.current_image_paths:
                QMessageBox.warning(self, "警告", "请先选择要插入的图片！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存图片！")
                return
                
            # 确保图片目录存在
            if not os.path.exists(self.images_dir):
                os.makedirs(self.images_dir)
                print(f"已创建图片目录: {self.images_dir}")
            
            # 检查目录权限
            if not os.access(self.images_dir, os.W_OK):
                print(f"错误: 图片目录无写入权限: {self.images_dir}")
                QMessageBox.critical(self, "错误", f"图片目录无写入权限: {self.images_dir}")
                return
            
            saved_count = 0
            failed_count = 0
            
            # 初始化图片列表
            if "images" not in data:
                data["images"] = []
            
            print(f"开始保存 {len(self.current_image_paths)} 张图片...")
            
            # 处理每张图片
            for i, image_path in enumerate(self.current_image_paths):
                try:
                    print(f"处理第 {i+1} 张图片: {image_path}")
                    
                    # 检查源文件是否存在
                    if not os.path.exists(image_path):
                        print(f"警告: 图片文件不存在: {image_path}")
                        failed_count += 1
                        continue
                    
                    # 检查源文件是否可读
                    if not os.access(image_path, os.R_OK):
                        print(f"警告: 图片文件无读取权限: {image_path}")
                        failed_count += 1
                        continue
                    
                    # 生成时间戳文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 包含毫秒
                    file_ext = os.path.splitext(image_path)[1]
                    new_filename = f"{timestamp}{file_ext}"
                    new_file_path = os.path.join(self.images_dir, new_filename)
                    
                    print(f"正在复制图片: {image_path} -> {new_file_path}")
                    
                    # 复制文件
                    shutil.copy2(image_path, new_file_path)
                    
                    # 验证文件是否复制成功
                    if not os.path.exists(new_file_path):
                        print(f"错误: 文件复制后不存在: {new_file_path}")
                        failed_count += 1
                        continue
                    
                    # 检查文件大小
                    original_size = os.path.getsize(image_path)
                    copied_size = os.path.getsize(new_file_path)
                    if original_size != copied_size:
                        print(f"错误: 文件大小不匹配: 原始={original_size}, 复制={copied_size}")
                        failed_count += 1
                        continue
                        
                    print(f"图片复制成功: {new_file_path} (大小: {copied_size} 字节)")
                    
                    # 添加到数据中
                    data["images"].append(new_filename)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"保存图片失败 {image_path}: {str(e)}")
                    failed_count += 1
            
            print(f"保存完成: 成功 {saved_count} 张, 失败 {failed_count} 张")
            
            # 保存数据并刷新显示
            self.save_data()
            self.load_images(data["images"])
            
            # 显示结果
            if saved_count > 0 and failed_count == 0:
                QMessageBox.information(self, "成功", f"成功保存 {saved_count} 张图片！")
            elif saved_count > 0 and failed_count > 0:
                QMessageBox.warning(self, "部分成功", f"成功保存 {saved_count} 张图片，{failed_count} 张图片保存失败！")
            else:
                QMessageBox.critical(self, "失败", f"所有图片保存失败！")
            
            # 清除已保存的图片路径
            self.current_image_paths = []
            
        except Exception as e:
            error_msg = f"保存图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def manage_images(self):
        """管理图片"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备管理图片！")
                return
            
            images = data.get("images", [])
            if not images:
                QMessageBox.information(self, "提示", "当前设备没有图片！")
                return
            
            # 创建图片管理对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("图片管理")
            dialog.setModal(True)
            dialog.setGeometry(200, 200, 500, 400)
            
            layout = QVBoxLayout()
            
            # 操作说明
            info_label = QLabel("按住Ctrl键可多选图片进行批量删除")
            info_label.setStyleSheet("color: blue; padding: 5px;")
            layout.addWidget(info_label)
            
            # 图片列表（支持多选）
            list_widget = QListWidget()
            list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            for image_filename in images:
                list_widget.addItem(image_filename)
            layout.addWidget(list_widget)
            
            # 按钮
            button_layout = QHBoxLayout()
            delete_btn = QPushButton("删除选中图片")
            delete_btn.clicked.connect(lambda: self.delete_selected_image(list_widget, data, dialog))
            batch_delete_btn = QPushButton("批量删除")
            batch_delete_btn.clicked.connect(lambda: self.batch_delete_images(list_widget, data, dialog))
            open_folder_btn = QPushButton("打开图片文件夹")
            open_folder_btn.clicked.connect(lambda: os.startfile(self.images_dir))
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(delete_btn)
            button_layout.addWidget(batch_delete_btn)
            button_layout.addWidget(open_folder_btn)
            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"管理图片失败: {str(e)}")
    
    def delete_selected_image(self, list_widget, data, dialog):
        """删除选中的图片"""
        try:
            current_item = list_widget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择要删除的图片！")
                return
            
            image_filename = current_item.text()
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除图片 '{image_filename}' 吗？\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 从数据中移除
                if "images" in data:
                    data["images"].remove(image_filename)
                
                # 删除文件
                image_path = os.path.join(self.images_dir, image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # 保存数据并刷新显示
                self.save_data()
                self.load_images(data.get("images", []))
                
                # 从列表中移除
                list_widget.takeItem(list_widget.row(current_item))
                
                QMessageBox.information(self, "成功", "图片已删除！")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除图片失败: {str(e)}")

    def batch_delete_images(self, list_widget, data, dialog):
        """批量删除图片"""
        try:
            selected_items = list_widget.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要删除的图片！")
                return
            
            image_filenames = [item.text() for item in selected_items]
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认批量删除", 
                f"确定要删除选中的 {len(image_filenames)} 张图片吗？\n\n选中的图片：\n" + 
                "\n".join([f"• {filename}" for filename in image_filenames[:5]]) + 
                (f"\n... 还有 {len(image_filenames) - 5} 张图片" if len(image_filenames) > 5 else "") +
                "\n\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                deleted_count = 0
                failed_count = 0
                
                for image_filename in image_filenames:
                    try:
                        # 从数据中移除
                        if "images" in data and image_filename in data["images"]:
                            data["images"].remove(image_filename)
                        
                        # 删除文件
                        image_path = os.path.join(self.images_dir, image_filename)
                        if os.path.exists(image_path):
                            os.remove(image_path)
                        
                        deleted_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        print(f"删除图片失败 {image_filename}: {str(e)}")
                
                # 保存数据并刷新显示
                self.save_data()
                self.load_images(data.get("images", []))
                
                # 从列表中移除已删除的项目
                for item in selected_items:
                    list_widget.takeItem(list_widget.row(item))
                
                # 显示结果
                if failed_count == 0:
                    QMessageBox.information(self, "成功", f"成功删除 {deleted_count} 张图片！")
                else:
                    QMessageBox.warning(self, "部分成功", 
                                      f"成功删除 {deleted_count} 张图片，{failed_count} 张删除失败。")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量删除图片失败: {str(e)}")

    def insert_principle_image(self):
        """插入原理图片"""
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "选择原理图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file_paths:
                self.current_principle_image_paths = file_paths
                QMessageBox.information(self, "提示", f"已选择 {len(file_paths)} 张原理图片，请点击保存按钮保存图片！")
        except Exception as e:
            error_msg = f"插入原理图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def save_principle_image(self):
        """保存原理图片"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            if not hasattr(self, 'current_principle_image_paths') or not self.current_principle_image_paths:
                QMessageBox.warning(self, "警告", "请先选择要插入的原理图片！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存原理图片！")
                return
                
            # 确保图片目录存在
            if not os.path.exists(self.images_dir):
                os.makedirs(self.images_dir)
                print(f"已创建图片目录: {self.images_dir}")
            
            # 检查目录权限
            if not os.access(self.images_dir, os.W_OK):
                print(f"错误: 图片目录无写入权限: {self.images_dir}")
                QMessageBox.critical(self, "错误", f"图片目录无写入权限: {self.images_dir}")
                return
            
            saved_count = 0
            failed_count = 0
            
            # 初始化图片列表
            if "principle_images" not in data:
                data["principle_images"] = []
            
            print(f"开始保存 {len(self.current_principle_image_paths)} 张原理图片...")
            
            # 处理每张图片
            for i, image_path in enumerate(self.current_principle_image_paths):
                try:
                    print(f"处理第 {i+1} 張原理圖片: {image_path}")
                    
                    # 检查源文件是否存在
                    if not os.path.exists(image_path):
                        print(f"警告: 原理图片文件不存在: {image_path}")
                        failed_count += 1
                        continue
                    
                    # 检查源文件是否可读
                    if not os.access(image_path, os.R_OK):
                        print(f"警告: 原理图片文件无读取权限: {image_path}")
                        failed_count += 1
                        continue
                    
                    # 生成时间戳文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 包含毫秒
                    file_ext = os.path.splitext(image_path)[1]
                    new_filename = f"principle_{timestamp}{file_ext}"
                    new_file_path = os.path.join(self.images_dir, new_filename)
                    
                    print(f"正在复制原理图片: {image_path} -> {new_file_path}")
                    
                    # 复制文件
                    shutil.copy2(image_path, new_file_path)
                    
                    # 验证文件是否复制成功
                    if not os.path.exists(new_file_path):
                        print(f"错误: 文件复制后不存在: {new_file_path}")
                        failed_count += 1
                        continue
                    
                    # 检查文件大小
                    original_size = os.path.getsize(image_path)
                    copied_size = os.path.getsize(new_file_path)
                    if original_size != copied_size:
                        print(f"错误: 文件大小不匹配: 原始={original_size}, 复制={copied_size}")
                        failed_count += 1
                        continue
                        
                    print(f"原理图片复制成功: {new_file_path} (大小: {copied_size} 字节)")
                    
                    # 添加到数据中
                    data["principle_images"].append(new_filename)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"保存原理图片失败 {image_path}: {str(e)}")
                    failed_count += 1
            
            print(f"原理图片保存完成: 成功 {saved_count} 张, 失败 {failed_count} 张")
            
            # 保存数据并刷新显示
            self.save_data()
            self.load_principle_images(data["principle_images"])
            
            # 显示结果
            if saved_count > 0 and failed_count == 0:
                QMessageBox.information(self, "成功", f"成功保存 {saved_count} 张原理图片！")
            elif saved_count > 0 and failed_count > 0:
                QMessageBox.warning(self, "部分成功", f"成功保存 {saved_count} 张原理图片，{failed_count} 张原理图片保存失败！")
            else:
                QMessageBox.critical(self, "失败", f"所有原理图片保存失败！")
            
            # 清除已保存的图片路径
            self.current_principle_image_paths = []
            
        except Exception as e:
            error_msg = f"保存原理图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def manage_principle_images(self):
        """管理原理图片"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备管理图片！")
                return
            
            images = data.get("principle_images", [])
            if not images:
                QMessageBox.information(self, "提示", "当前设备没有原理图片！")
                return
            
            # 创建图片管理对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("原理图片管理")
            dialog.setModal(True)
            dialog.setGeometry(200, 200, 500, 400)
            
            layout = QVBoxLayout()
            
            # 操作说明
            info_label = QLabel("按住Ctrl键可多选图片进行批量删除")
            info_label.setStyleSheet("color: blue; padding: 5px;")
            layout.addWidget(info_label)
            
            # 图片列表（支持多选）
            list_widget = QListWidget()
            list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            for image_filename in images:
                list_widget.addItem(image_filename)
            layout.addWidget(list_widget)
            
            # 按钮
            button_layout = QHBoxLayout()
            delete_btn = QPushButton("删除选中图片")
            delete_btn.clicked.connect(lambda: self.delete_selected_principle_image(list_widget, data, dialog))
            batch_delete_btn = QPushButton("批量删除")
            batch_delete_btn.clicked.connect(lambda: self.batch_delete_principle_images(list_widget, data, dialog))
            open_folder_btn = QPushButton("打开图片文件夹")
            open_folder_btn.clicked.connect(lambda: os.startfile(self.images_dir))
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            
            button_layout.addWidget(delete_btn)
            button_layout.addWidget(batch_delete_btn)
            button_layout.addWidget(open_folder_btn)
            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"管理原理图片失败: {str(e)}")
    
    def delete_selected_principle_image(self, list_widget, data, dialog):
        """删除选中的原理图片"""
        try:
            current_item = list_widget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择要删除的图片！")
                return
            
            image_filename = current_item.text()
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除原理图片 '{image_filename}' 吗？\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 从数据中移除
                if "principle_images" in data:
                    data["principle_images"].remove(image_filename)
                
                # 删除文件
                image_path = os.path.join(self.images_dir, image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # 保存数据并刷新显示
                self.save_data()
                self.load_principle_images(data.get("principle_images", []))
                
                # 从列表中移除
                list_widget.takeItem(list_widget.row(current_item))
                
                QMessageBox.information(self, "成功", "原理图片已删除！")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除原理图片失败: {str(e)}")

    def batch_delete_principle_images(self, list_widget, data, dialog):
        """批量删除原理图片"""
        try:
            selected_items = list_widget.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要删除的图片！")
                return
            
            image_filenames = [item.text() for item in selected_items]
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认批量删除", 
                f"确定要删除选中的 {len(image_filenames)} 张原理图片吗？\n\n选中的图片：\n" + 
                "\n".join([f"• {filename}" for filename in image_filenames[:5]]) + 
                (f"\n... 还有 {len(image_filenames) - 5} 张图片" if len(image_filenames) > 5 else "") +
                "\n\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                deleted_count = 0
                failed_count = 0
                
                for image_filename in image_filenames:
                    try:
                        # 从数据中移除
                        if "principle_images" in data and image_filename in data["principle_images"]:
                            data["principle_images"].remove(image_filename)
                        
                        # 删除文件
                        image_path = os.path.join(self.images_dir, image_filename)
                        if os.path.exists(image_path):
                            os.remove(image_path)
                        
                        deleted_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        print(f"删除原理图片失败 {image_filename}: {str(e)}")
                
                # 保存数据并刷新显示
                self.save_data()
                self.load_principle_images(data.get("principle_images", []))
                
                # 从列表中移除已删除的项目
                for item in selected_items:
                    list_widget.takeItem(list_widget.row(item))
                
                # 显示结果
                if failed_count == 0:
                    QMessageBox.information(self, "成功", f"成功删除 {deleted_count} 张原理图片！")
                else:
                    QMessageBox.warning(self, "部分成功", 
                                      f"成功删除 {deleted_count} 张原理图片，{failed_count} 张删除失败。")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量删除原理图片失败: {str(e)}")

    def insert_supplier_image(self):
        """插入供应商图片"""
        try:
            # 检查是否有选中的项目
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个产品！")
                return
                
            # 检查是否有选中的供应商
            supplier_row = self.get_current_supplier_row()
            if supplier_row < 0:
                QMessageBox.warning(self, "警告", "请先选择一个供应商！\n\n操作步骤：\n1. 在供应商表格中点击选择一个供应商\n2. 或者双击供应商表格中的供应商来管理其图片")
                return
                
            print(f"开始插入供应商图片，当前供应商行: {supplier_row}")
            
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "选择供应商图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file_paths:
                self.current_supplier_image_paths = file_paths
                print(f"已选择 {len(file_paths)} 张供应商图片")
                QMessageBox.information(self, "成功", f"已选择 {len(file_paths)} 张图片，请点击'保存供应商图片'按钮来保存。")
            else:
                print("用户取消了图片选择")
        except Exception as e:
            error_msg = f"插入供应商图片失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", error_msg)

    def save_supplier_image(self):
        """保存供应商图片"""
        try:
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个设备！")
                return
                
            if not hasattr(self, 'current_supplier_image_paths') or not self.current_supplier_image_paths:
                QMessageBox.warning(self, "警告", "请先选择要插入的供应商图片！\n\n操作步骤：\n1. 点击'插入供应商图片'按钮\n2. 选择要插入的图片文件\n3. 然后点击'保存供应商图片'按钮")
                return
                
            # 检查目录写入权限
            if not os.access(self.images_dir, os.W_OK):
                QMessageBox.warning(self, "警告", "图片目录没有写入权限！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能为具体设备保存供应商图片！")
                return
                
            # 确保图片目录存在
            if not os.path.exists(self.images_dir):
                os.makedirs(self.images_dir, exist_ok=True)
                print(f"已创建图片目录: {self.images_dir}")
                
            # 获取当前选中的供应商行
            supplier_row = self.get_current_supplier_row()
            if supplier_row >= 0:
                print(f"保存供应商图片: 当前供应商行: {supplier_row}")
            else:
                QMessageBox.warning(self, "警告", "请先选择一个供应商！\n\n操作步骤：\n1. 在供应商表格中点击选择一个供应商\n2. 或者双击供应商表格中的供应商来管理其图片")
                return
                
            saved_count = 0
            failed_count = 0
            
            # 处理多张图片
            for image_path in self.current_supplier_image_paths:
                try:
                    # 检查源文件是否存在和可读
                    if not os.path.exists(image_path):
                        print(f"源文件不存在: {image_path}")
                        failed_count += 1
                        continue
                        
                    if not os.access(image_path, os.R_OK):
                        print(f"源文件不可读: {image_path}")
                        failed_count += 1
                        continue
                    
                    # 生成时间戳文件名（包含毫秒）
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    file_ext = os.path.splitext(image_path)[1]
                    new_filename = f"supplier_{timestamp}{file_ext}"
                    new_file_path = os.path.join(self.images_dir, new_filename)
                    
                    print(f"正在复制供应商图片: {image_path} -> {new_file_path}")
                    
                    # 复制文件
                    shutil.copy2(image_path, new_file_path)
                    
                    # 验证文件是否复制成功
                    if not os.path.exists(new_file_path):
                        print(f"文件复制后不存在: {new_file_path}")
                        failed_count += 1
                        continue
                    
                    # 验证文件大小
                    original_size = os.path.getsize(image_path)
                    copied_size = os.path.getsize(new_file_path)
                    if original_size != copied_size:
                        print(f"文件大小不匹配: 原始={original_size}, 复制={copied_size}")
                        failed_count += 1
                        continue
                        
                    print(f"供应商图片复制成功: {new_file_path}")
                    
                    # 更新特定供应商的图片数据
                    if "pricing" in data and "suppliers" in data["pricing"]:
                        suppliers = data["pricing"]["suppliers"]
                        if supplier_row < len(suppliers):
                            if "images" not in suppliers[supplier_row]:
                                suppliers[supplier_row]["images"] = []
                            suppliers[supplier_row]["images"].append(new_filename)
                            print(f"已为供应商 '{suppliers[supplier_row]['name']}' 添加图片: {new_filename}")
                    else:
                        print("警告: 无法确定当前供应商")
                        # 如果没有选中供应商，添加到全局供应商图片（向后兼容）
                        if "supplier_images" not in data:
                            data["supplier_images"] = []
                        data["supplier_images"].append(new_filename)
                    
                    saved_count += 1
                    
                except Exception as e:
                    print(f"保存供应商图片失败 {image_path}: {str(e)}")
                    failed_count += 1
            
            # 保存数据并刷新显示
            if saved_count > 0:
                self.save_data()
                # 刷新当前供应商的图片显示
                supplier_row = self.get_current_supplier_row()
                if supplier_row >= 0:
                    self.load_supplier_images_for_specific_supplier(supplier_row)
                # 刷新供应商表格中的图片信息
                self.load_pricing(data.get("pricing", {}))
            
            # 显示结果
            if saved_count > 0 and failed_count == 0:
                QMessageBox.information(self, "成功", f"成功保存 {saved_count} 张供应商图片！")
            elif saved_count > 0 and failed_count > 0:
                QMessageBox.warning(self, "部分成功", f"成功保存 {saved_count} 张，失败 {failed_count} 张供应商图片")
            else:
                QMessageBox.warning(self, "失败", f"保存供应商图片失败，共 {failed_count} 张")
            
            # 清空当前选择的图片路径
            self.current_supplier_image_paths = []
            
        except Exception as e:
            error_msg = f"保存供应商图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def delete_selected_supplier_image(self, list_widget, supplier, dialog, supplier_row):
        """删除选中的供应商图片"""
        try:
            current_item = list_widget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择要删除的图片！")
                return
            
            image_name = current_item.text()
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除供应商图片 '{image_name}' 吗？",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 从供应商数据中移除
                if "images" in supplier and image_name in supplier["images"]:
                    supplier["images"].remove(image_name)
                    print(f"已从供应商 '{supplier.get('name', '未知')}' 移除图片: {image_name}")
                
                # 删除物理文件
                image_path = os.path.join(self.images_dir, image_name)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"已删除供应商图片文件: {image_path}")
                
                # 保存数据
                self.save_data()
                
                # 刷新显示
                self.load_supplier_images_for_specific_supplier(supplier_row)
                # 刷新供应商表格中的图片信息
                if self.current_item:
                    path = self.get_item_path(self.current_item)
                    data = self.get_data_by_path(path)
                    if data:
                        self.load_pricing(data.get("pricing", {}))
                
                # 从列表中移除
                list_widget.takeItem(list_widget.row(current_item))
                
                QMessageBox.information(self, "成功", "供应商图片已删除！")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除供应商图片失败: {str(e)}")

    def batch_delete_supplier_images(self, list_widget, supplier, dialog, supplier_row):
        """批量删除供应商图片"""
        try:
            selected_items = list_widget.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要删除的图片！")
                return
            
            image_names = [item.text() for item in selected_items]
            supplier_name = supplier.get("name", "未知供应商")
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认批量删除", 
                f"确定要删除供应商 '{supplier_name}' 的 {len(image_names)} 张图片吗？\n\n选中的图片：\n" + 
                "\n".join([f"• {filename}" for filename in image_names[:5]]) + 
                (f"\n... 还有 {len(image_names) - 5} 张图片" if len(image_names) > 5 else "") +
                "\n\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                deleted_count = 0
                failed_count = 0
                
                for image_name in image_names:
                    try:
                        # 从供应商数据中移除
                        if "images" in supplier and image_name in supplier["images"]:
                            supplier["images"].remove(image_name)
                            print(f"已从供应商 '{supplier_name}' 移除图片: {image_name}")
                        
                        # 删除物理文件
                        image_path = os.path.join(self.images_dir, image_name)
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            print(f"已删除供应商图片文件: {image_path}")
                        
                        deleted_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        print(f"删除供应商图片失败 {image_name}: {str(e)}")
                
                # 保存数据
                self.save_data()
                
                # 刷新显示
                self.load_supplier_images_for_specific_supplier(supplier_row)
                # 刷新供应商表格中的图片信息
                if self.current_item:
                    path = self.get_item_path(self.current_item)
                    data = self.get_data_by_path(path)
                    if data:
                        self.load_pricing(data.get("pricing", {}))
                
                # 从列表中移除已删除的项目
                for item in selected_items:
                    list_widget.takeItem(list_widget.row(item))
                
                # 显示结果
                if failed_count == 0:
                    QMessageBox.information(self, "成功", f"成功删除供应商 '{supplier_name}' 的 {deleted_count} 张图片！")
                else:
                    QMessageBox.warning(self, "部分成功", 
                                      f"成功删除供应商 '{supplier_name}' 的 {deleted_count} 张图片，{failed_count} 张删除失败。")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量删除供应商图片失败: {str(e)}")

    def on_supplier_table_double_clicked(self, item):
        """处理供应商表格双击事件"""
        try:
            row = item.row()
            
            # 验证行索引
            if row < 0 or row >= self.supplier_table.rowCount():
                QMessageBox.warning(self, "警告", "无效的供应商行索引")
                return
            
            # 获取供应商名称（第1列）
            supplier_name_item = self.supplier_table.item(row, 1)
            supplier_name = supplier_name_item.text().strip() if supplier_name_item else ""
            
            # 如果供应商名称为空，直接进入编辑模式
            if not supplier_name:
                print(f"供应商行 {row} 名称为空，进入编辑模式")
                self.edit_supplier_dialog(row)
                return
            
            # 设置当前选中的供应商行，然后打开图片管理对话框
            self.current_supplier_row = row
            print(f"双击供应商 '{supplier_name}'，打开图片管理对话框")
            self.manage_supplier_images()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理供应商选择时发生错误: {str(e)}")
            print(f"供应商双击事件错误: {e}")
            import traceback
            traceback.print_exc()

    def load_supplier_images_for_specific_supplier(self, supplier_row):
        """加载特定供应商的图片"""
        try:
            if not self.current_item:
                return
                
            path = self.get_item_path(self.current_item)
            data = self.get_data_by_path(path)
            
            if not data or "pricing" not in data:
                return
                
            suppliers = data["pricing"].get("suppliers", [])
            if supplier_row >= len(suppliers):
                return
                
            supplier = suppliers[supplier_row]
            supplier_images = supplier.get("images", [])
            
            print(f"加载供应商 '{supplier.get('name', '')}' 的图片，共 {len(supplier_images)} 张")
            
            # 清除现有缩略图
            while self.supplier_image_thumbnail_layout.count() > 0:
                item = self.supplier_image_thumbnail_layout.takeAt(0)
                if item.widget():
                    if item.widget() != self.supplier_image_thumbnail_label:
                        item.widget().deleteLater()
            
            if supplier_images and len(supplier_images) > 0:
                self.supplier_image_thumbnail_label.hide()
                
                # 验证图片文件并过滤掉不存在的文件
                valid_images = []
                for image_filename in supplier_images:
                    image_path = os.path.join(self.images_dir, image_filename)
                    if os.path.exists(image_path) and os.access(image_path, os.R_OK) and os.path.getsize(image_path) > 0:
                        valid_images.append(image_filename)
                
                # 为每张有效图片创建缩略图
                for i, image_filename in enumerate(valid_images):
                    try:
                        image_path = os.path.join(self.images_dir, image_filename)
                        # 创建完整的图片路径列表用于导航
                        full_image_paths = [os.path.join(self.images_dir, img) for img in valid_images]
                        thumbnail_widget = ImageThumbnailWidget(image_path, full_image_paths, i, self.supplier_image_thumbnail_container, self.delete_supplier_image_callback)
                        self.supplier_image_thumbnail_layout.addWidget(thumbnail_widget)
                    except Exception as e:
                        print(f"创建供应商图片缩略图失败: {str(e)}")
                        continue
                
                # 添加弹性空间
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.supplier_image_thumbnail_layout.addItem(spacer)
                
                if len(valid_images) == 0:
                    self.supplier_image_thumbnail_label.show()
                    self.supplier_image_thumbnail_label.setText("所有供应商图片文件均缺失")
            else:
                self.supplier_image_thumbnail_label.show()
                self.supplier_image_thumbnail_label.setText("暂无供应商图片，点击下方按钮添加图片")
                
        except Exception as e:
            print(f"加载供应商图片失败: {str(e)}")
    
    def edit_supplier_dialog(self, row):
        """编辑供应商信息的简单对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout
            
            # 验证行索引
            if row < 0 or row >= self.supplier_table.rowCount():
                QMessageBox.warning(self, "警告", "无效的供应商行索引")
                return
            
            # 获取当前供应商信息
            supplier_name_item = self.supplier_table.item(row, 1)
            price_item = self.supplier_table.item(row, 2)
            lead_time_item = self.supplier_table.item(row, 3)
            contact_item = self.supplier_table.item(row, 4)
            
            current_name = supplier_name_item.text() if supplier_name_item else ""
            current_price = price_item.text() if price_item else ""
            current_lead_time = lead_time_item.text() if lead_time_item else ""
            current_contact = contact_item.text() if contact_item else ""
            
            # 创建编辑对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(f"编辑供应商信息 - 第{row+1}行")
            dialog.setModal(True)
            dialog.resize(450, 350)
            dialog.setMinimumSize(400, 300)
            
            layout = QVBoxLayout()
            
            # 使用表单布局，更整洁
            form_layout = QFormLayout()
            
            # 供应商名称
            name_edit = QLineEdit(current_name)
            name_edit.setPlaceholderText("请输入供应商名称")
            name_edit.setMinimumWidth(250)
            form_layout.addRow("供应商名称:", name_edit)
            
            # 价格
            price_edit = QLineEdit(current_price)
            price_edit.setPlaceholderText("请输入价格（数字）")
            price_edit.setMinimumWidth(250)
            form_layout.addRow("价格:", price_edit)
            
            # 供货周期
            lead_time_edit = QLineEdit(current_lead_time)
            lead_time_edit.setPlaceholderText("例如：7天、2周等")
            lead_time_edit.setMinimumWidth(250)
            form_layout.addRow("供货周期:", lead_time_edit)
            
            # 联系方式
            contact_edit = QLineEdit(current_contact)
            contact_edit.setPlaceholderText("例如：张经理 13800138000")
            contact_edit.setMinimumWidth(250)
            form_layout.addRow("联系方式:", contact_edit)
            
            layout.addLayout(form_layout)
            
            # 添加一些间距
            layout.addSpacing(20)
            
            # 按钮
            button_layout = QHBoxLayout()
            save_btn = QPushButton("保存")
            save_btn.setDefault(True)
            save_btn.setMinimumWidth(80)
            cancel_btn = QPushButton("取消")
            cancel_btn.setMinimumWidth(80)
            
            button_layout.addStretch()
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # 连接信号
            def save_supplier():
                try:
                    # 数据验证
                    name = name_edit.text().strip()
                    price_text = price_edit.text().strip()
                    lead_time = lead_time_edit.text().strip()
                    contact = contact_edit.text().strip()
                    
                    # 验证供应商名称
                    if not name:
                        QMessageBox.warning(dialog, "验证失败", "供应商名称不能为空")
                        name_edit.setFocus()
                        return
                    
                    # 验证价格
                    try:
                        if price_text:
                            price = float(price_text)
                            if price < 0:
                                QMessageBox.warning(dialog, "验证失败", "价格不能为负数")
                                price_edit.setFocus()
                                return
                        else:
                            price = 0
                    except ValueError:
                        QMessageBox.warning(dialog, "验证失败", "价格必须是有效的数字")
                        price_edit.setFocus()
                        return
                    
                    # 更新表格数据
                    self.supplier_table.setItem(row, 1, QTableWidgetItem(name))
                    self.supplier_table.setItem(row, 2, QTableWidgetItem(str(price)))
                    self.supplier_table.setItem(row, 3, QTableWidgetItem(lead_time))
                    self.supplier_table.setItem(row, 4, QTableWidgetItem(contact))
                    
                    # 触发自动保存
                    try:
                        self.auto_save_pricing()
                    except Exception as auto_save_error:
                        print(f"自动保存失败: {auto_save_error}")
                        # 即使自动保存失败，也继续保存到表格
                    
                    dialog.accept()
                    QMessageBox.information(self, "成功", f"供应商 '{name}' 信息已保存")
                    
                except Exception as e:
                    QMessageBox.critical(dialog, "错误", f"保存供应商信息失败: {str(e)}")
                    print(f"保存供应商信息错误: {e}")
                    import traceback
                    traceback.print_exc()
            
            def cancel_edit():
                dialog.reject()
            
            # 连接按钮信号
            save_btn.clicked.connect(save_supplier)
            cancel_btn.clicked.connect(cancel_edit)
            
            # 连接回车键
            name_edit.returnPressed.connect(save_supplier)
            price_edit.returnPressed.connect(save_supplier)
            lead_time_edit.returnPressed.connect(save_supplier)
            contact_edit.returnPressed.connect(save_supplier)
            
            # 设置焦点到第一个输入框
            name_edit.setFocus()
            name_edit.selectAll()
            
            # 显示对话框
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                print(f"供应商信息编辑成功，行 {row}")
            else:
                print(f"供应商信息编辑取消，行 {row}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建供应商编辑对话框失败: {str(e)}")
            print(f"供应商编辑对话框错误: {e}")
            import traceback
            traceback.print_exc()

    def get_current_supplier_row(self):
        """获取当前选中的供应商行"""
        try:
            if not self.current_item:
                print("获取当前供应商行: 没有选中项目")
                return -1
                
            path = self.get_item_path(self.current_item)
            data = self.get_data_by_path(path)
            
            if not data or "pricing" not in data:
                print("获取当前供应商行: 数据无效或没有价格信息")
                return -1
                
            # 首先尝试从供应商表格的选中行获取
            current_row = self.supplier_table.currentRow()
            if current_row >= 0:
                print(f"获取当前供应商行: 从表格选中行获取，行号: {current_row}")
                return current_row
                
            # 如果表格没有选中行，尝试从当前供应商信息标签获取
            if hasattr(self, 'current_supplier_info') and self.current_supplier_info:
                try:
                    current_supplier_name = self.current_supplier_info.text()
                    print(f"获取当前供应商行: 从标签获取供应商名称: {current_supplier_name}")
                    if "正在管理供应商 '" in current_supplier_name:
                        supplier_name = current_supplier_name.split("'")[1]
                        suppliers = data["pricing"].get("suppliers", [])
                        for i, supplier in enumerate(suppliers):
                            if supplier.get("name") == supplier_name:
                                print(f"获取当前供应商行: 找到供应商 '{supplier_name}' 在第 {i} 行")
                                return i
                except Exception as label_error:
                    print(f"获取当前供应商行: 从标签获取失败: {str(label_error)}")
            
            print("获取当前供应商行: 无法确定当前供应商")
            return -1
        except Exception as e:
            print(f"获取当前供应商行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1

    def toggle_supplier_image_section(self):
        """切换供应商图片区域的显示状态"""
        if self.supplier_image_expand_btn.isChecked():
            self.supplier_image_section.show()
            self.supplier_image_expand_btn.setText("收起图片管理")
        else:
            self.supplier_image_section.hide()
            self.supplier_image_expand_btn.setText("展开图片管理")

    def manage_supplier_images(self):
        """管理供应商图片"""
        try:
            # 获取当前选中的供应商
            supplier_row = self.get_current_supplier_row()
            if supplier_row < 0:
                QMessageBox.warning(self, "警告", "请先双击选择一个供应商")
                return
            
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个项目")
                return
            
            path = self.get_item_path(self.current_item)
            data = self.get_data_by_path(path)
            
            if not data or "pricing" not in data:
                QMessageBox.warning(self, "警告", "无法获取项目数据")
                return
            
            suppliers = data["pricing"].get("suppliers", [])
            if supplier_row >= len(suppliers):
                QMessageBox.warning(self, "警告", "供应商数据无效")
                return
            
            supplier = suppliers[supplier_row]
            supplier_name = supplier.get("name", "未知供应商")
            supplier_images = supplier.get("images", [])
            
            # 创建管理对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(f"管理供应商 '{supplier_name}' 的图片")
            dialog.setModal(True)
            dialog.setGeometry(200, 200, 600, 500)
            
            layout = QVBoxLayout()
            
            # 供应商信息
            info_label = QLabel(f"供应商: {supplier_name}")
            info_label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f0f8ff; border-radius: 5px;")
            layout.addWidget(info_label)
            
            # 操作说明
            operation_label = QLabel("按住Ctrl键可多选图片进行批量删除")
            operation_label.setStyleSheet("color: blue; padding: 5px;")
            layout.addWidget(operation_label)
            
            # 图片列表（支持多选）
            list_widget = QListWidget()
            list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            for image in supplier_images:
                list_widget.addItem(image)
            layout.addWidget(list_widget)
            
            # 按钮布局
            btn_layout = QHBoxLayout()
            
            # 插入图片按钮
            insert_btn = QPushButton("插入供应商图片")
            insert_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")
            insert_btn.clicked.connect(lambda: self.insert_supplier_image_from_dialog(dialog, supplier_row))
            
            # 保存图片按钮
            save_btn = QPushButton("保存供应商图片")
            save_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 4px;")
            save_btn.clicked.connect(lambda: self.save_supplier_image_from_dialog(dialog, supplier_row))
            
            # 删除按钮
            delete_btn = QPushButton("删除选中图片")
            delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 4px;")
            delete_btn.clicked.connect(lambda: self.delete_selected_supplier_image(list_widget, supplier, dialog, supplier_row))
            
            # 批量删除按钮
            batch_delete_btn = QPushButton("批量删除")
            batch_delete_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 8px; border-radius: 4px;")
            batch_delete_btn.clicked.connect(lambda: self.batch_delete_supplier_images(list_widget, supplier, dialog, supplier_row))
            
            # 打开文件夹按钮
            open_folder_btn = QPushButton("打开图片文件夹")
            open_folder_btn.clicked.connect(lambda: os.startfile(self.images_dir))
            
            # 关闭按钮
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(insert_btn)
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addWidget(batch_delete_btn)
            btn_layout.addWidget(open_folder_btn)
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"管理供应商图片时发生错误: {str(e)}")

    def insert_supplier_image_from_dialog(self, dialog, supplier_row):
        """从对话框插入供应商图片"""
        try:
            # 检查是否有选中的项目
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个产品！")
                return
                
            print(f"开始插入供应商图片，当前供应商行: {supplier_row}")
            
            file_paths, _ = QFileDialog.getOpenFileNames(
                dialog, "选择供应商图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file_paths:
                self.current_supplier_image_paths = file_paths
                print(f"已选择 {len(file_paths)} 张供应商图片")
                QMessageBox.information(dialog, "成功", f"已选择 {len(file_paths)} 张图片，请点击'保存供应商图片'按钮来保存。")
            else:
                print("用户取消了图片选择")
        except Exception as e:
            error_msg = f"插入供应商图片失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(dialog, "错误", error_msg)

    def save_supplier_image_from_dialog(self, dialog, supplier_row):
        """从对话框保存供应商图片"""
        try:
            if not self.current_item:
                QMessageBox.warning(dialog, "警告", "请先选择一个设备！")
                return
                
            if not hasattr(self, 'current_supplier_image_paths') or not self.current_supplier_image_paths:
                QMessageBox.warning(dialog, "警告", "请先选择要插入的供应商图片！\n\n操作步骤：\n1. 点击'插入供应商图片'按钮\n2. 选择要插入的图片文件\n3. 然后点击'保存供应商图片'按钮")
                return
                
            # 检查目录写入权限
            if not os.access(self.images_dir, os.W_OK):
                QMessageBox.warning(dialog, "警告", "图片目录没有写入权限！")
                return
                
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(dialog, "警告", "无法获取设备路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(dialog, "警告", "无法找到设备数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(dialog, "警告", "只能为具体设备保存供应商图片！")
                return
                
            # 确保图片目录存在
            if not os.path.exists(self.images_dir):
                os.makedirs(self.images_dir, exist_ok=True)
                print(f"已创建图片目录: {self.images_dir}")
                
            print(f"保存供应商图片: 当前供应商行: {supplier_row}")
                
            saved_count = 0
            failed_count = 0
            
            # 处理多张图片
            for image_path in self.current_supplier_image_paths:
                try:
                    # 检查源文件是否存在和可读
                    if not os.path.exists(image_path):
                        print(f"源文件不存在: {image_path}")
                        failed_count += 1
                        continue
                        
                    if not os.access(image_path, os.R_OK):
                        print(f"源文件不可读: {image_path}")
                        failed_count += 1
                        continue
                    
                    # 生成时间戳文件名（包含毫秒）
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    file_ext = os.path.splitext(image_path)[1]
                    new_filename = f"supplier_{timestamp}{file_ext}"
                    new_file_path = os.path.join(self.images_dir, new_filename)
                    
                    print(f"正在复制供应商图片: {image_path} -> {new_file_path}")
                    
                    # 复制文件
                    shutil.copy2(image_path, new_file_path)
                    
                    # 验证文件是否复制成功
                    if not os.path.exists(new_file_path):
                        print(f"文件复制后不存在: {new_file_path}")
                        failed_count += 1
                        continue
                    
                    # 验证文件大小
                    original_size = os.path.getsize(image_path)
                    copied_size = os.path.getsize(new_file_path)
                    if original_size != copied_size:
                        print(f"文件大小不匹配: 原始={original_size}, 复制={copied_size}")
                        failed_count += 1
                        continue
                        
                    print(f"供应商图片复制成功: {new_file_path}")
                    
                    # 更新特定供应商的图片数据
                    if "pricing" in data and "suppliers" in data["pricing"]:
                        suppliers = data["pricing"]["suppliers"]
                        if supplier_row < len(suppliers):
                            if "images" not in suppliers[supplier_row]:
                                suppliers[supplier_row]["images"] = []
                            suppliers[supplier_row]["images"].append(new_filename)
                            print(f"已为供应商 '{suppliers[supplier_row]['name']}' 添加图片: {new_filename}")
                    else:
                        print("警告: 无法确定当前供应商")
                        # 如果没有选中供应商，添加到全局供应商图片（向后兼容）
                        if "supplier_images" not in data:
                            data["supplier_images"] = []
                        data["supplier_images"].append(new_filename)
                    
                    saved_count += 1
                    
                except Exception as e:
                    print(f"保存供应商图片失败 {image_path}: {str(e)}")
                    failed_count += 1
            
            # 保存数据并刷新显示
            if saved_count > 0:
                self.save_data()
                # 刷新供应商表格中的图片信息
                self.load_pricing(data.get("pricing", {}))
                # 重新打开对话框以刷新图片列表
                dialog.close()
                self.manage_supplier_images()
            
            # 显示结果
            if saved_count > 0 and failed_count == 0:
                QMessageBox.information(dialog, "成功", f"成功保存 {saved_count} 张供应商图片！")
            elif saved_count > 0 and failed_count > 0:
                QMessageBox.warning(dialog, "部分成功", f"成功保存 {saved_count} 张，失败 {failed_count} 张供应商图片")
            else:
                QMessageBox.warning(dialog, "失败", f"保存供应商图片失败，共 {failed_count} 张")
            
            # 清空当前选择的图片路径
            self.current_supplier_image_paths = []
            
        except Exception as e:
            error_msg = f"保存供应商图片失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(dialog, "错误", error_msg)

    def debug_image_saving(self):
        """调试图片保存功能"""
        try:
            debug_info = []
            debug_info.append("=== 图片保存调试信息 ===")
            
            # 检查当前选中的设备
            if not self.current_item:
                debug_info.append("❌ 未选择任何设备")
            else:
                path = self.get_item_path(self.current_item)
                debug_info.append(f"✅ 当前设备路径: {path}")
                
                data = self.get_data_by_path(path)
                if data:
                    debug_info.append(f"✅ 设备数据获取成功")
                    
                    # 检查图片目录
                    debug_info.append(f"📁 图片目录: {self.images_dir}")
                    if os.path.exists(self.images_dir):
                        debug_info.append(f"✅ 图片目录存在")
                        if os.access(self.images_dir, os.W_OK):
                            debug_info.append(f"✅ 图片目录可写")
                        else:
                            debug_info.append(f"❌ 图片目录不可写")
                    else:
                        debug_info.append(f"❌ 图片目录不存在")
                    
                    # 检查一般图片
                    images = data.get("images", [])
                    debug_info.append(f"📸 一般图片数量: {len(images)}")
                    for i, img in enumerate(images):
                        img_path = os.path.join(self.images_dir, img)
                        if os.path.exists(img_path):
                            debug_info.append(f"  ✅ 图片 {i+1}: {img} (存在)")
                        else:
                            debug_info.append(f"  ❌ 图片 {i+1}: {img} (不存在)")
                    
                    # 检查原理图片
                    principle_images = data.get("principle_images", [])
                    debug_info.append(f"🔬 原理图片数量: {len(principle_images)}")
                    for i, img in enumerate(principle_images):
                        img_path = os.path.join(self.images_dir, img)
                        if os.path.exists(img_path):
                            debug_info.append(f"  ✅ 原理图片 {i+1}: {img} (存在)")
                        else:
                            debug_info.append(f"  ❌ 原理图片 {i+1}: {img} (不存在)")
                    
                    # 检查供应商图片
                    supplier_images = data.get("supplier_images", [])
                    debug_info.append(f"🏢 供应商图片数量: {len(supplier_images)}")
                    for i, img in enumerate(supplier_images):
                        img_path = os.path.join(self.images_dir, img)
                        if os.path.exists(img_path):
                            debug_info.append(f"  ✅ 供应商图片 {i+1}: {img} (存在)")
                        else:
                            debug_info.append(f"  ❌ 供应商图片 {i+1}: {img} (不存在)")
                else:
                    debug_info.append("❌ 无法获取设备数据")
            
            # 检查当前选择的图片
            if hasattr(self, 'current_image_paths') and self.current_image_paths:
                debug_info.append(f"📋 当前选择的一般图片: {len(self.current_image_paths)} 张")
                for i, path in enumerate(self.current_image_paths):
                    if os.path.exists(path):
                        debug_info.append(f"  ✅ 选择图片 {i+1}: {path} (存在)")
                    else:
                        debug_info.append(f"  ❌ 选择图片 {i+1}: {path} (不存在)")
            else:
                debug_info.append("📋 未选择一般图片")
            
            if hasattr(self, 'current_principle_image_paths') and self.current_principle_image_paths:
                debug_info.append(f"📋 当前选择的原理图片: {len(self.current_principle_image_paths)} 张")
                for i, path in enumerate(self.current_principle_image_paths):
                    if os.path.exists(path):
                        debug_info.append(f"  ✅ 选择原理图片 {i+1}: {path} (存在)")
                    else:
                        debug_info.append(f"  ❌ 选择原理图片 {i+1}: {path} (不存在)")
            else:
                debug_info.append("📋 未选择原理图片")
            
            # 显示调试信息
            debug_text = "\n".join(debug_info)
            print(debug_text)
            
            # 创建调试信息对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("图片保存调试信息")
            dialog.setModal(True)
            dialog.setGeometry(100, 100, 600, 400)
            
            layout = QVBoxLayout()
            
            # 调试信息文本框
            text_edit = QTextEdit()
            text_edit.setPlainText(debug_text)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            
            # 关闭按钮
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            error_msg = f"调试图片保存功能失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def export_data(self):
        """导出数据"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "", "JSON文件 (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.system_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", "数据导出成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def import_data(self):
        """导入数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入数据", "", "JSON文件 (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                
                reply = QMessageBox.question(
                    self, "确认导入", 
                    "导入数据将覆盖当前数据，确定继续吗？"
                )
                if reply == QMessageBox.Yes:
                    self.system_data = imported_data
                    self.save_data()
                    self.init_tree()
                    self.update_tag_index()
                    QMessageBox.information(self, "成功", "数据导入成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tree.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # 添加分类
        add_category_action = menu.addAction("添加分类")
        add_category_action.triggered.connect(lambda: self.add_category_from_context(item))
        
        # 添加设备
        add_item_action = menu.addAction("添加设备")
        add_item_action.triggered.connect(lambda: self.add_item_from_context(item))
        
        menu.addSeparator()
        
        # 重命名
        rename_action = menu.addAction("重命名")
        rename_action.triggered.connect(lambda: self.rename_category_from_context(item))
        
        # 删除
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self.delete_category_from_context(item))
        
        # 显示菜单
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def add_category_from_context(self, item):
        """从右键菜单添加分类"""
        name, ok = QInputDialog.getText(self, "添加分类", "请输入分类名称:")
        if ok and name:
            parent_path = self.get_item_path(item)
            self.add_category_to_data(parent_path, name)
            
            # 记住当前展开状态
            expanded_items = self.get_expanded_items()
            
            # 重新构建树
            self.init_tree()
            
            # 恢复展开状态
            self.restore_expanded_items(expanded_items)
            
            # 展开新添加的分类
            self.expand_new_item(parent_path + [name])
            
            self.save_data()

    def add_item_from_context(self, item):
        """从右键菜单添加设备"""
        name, ok = QInputDialog.getText(self, "添加设备", "请输入设备名称:")
        if ok and name:
            parent_path = self.get_item_path(item)
            self.add_item_to_data(parent_path, name)
            
            # 记住当前展开状态
            expanded_items = self.get_expanded_items()
            
            # 重新构建树
            self.init_tree()
            
            # 恢复展开状态
            self.restore_expanded_items(expanded_items)
            
            # 展开新添加的项目
            self.expand_new_item(parent_path + [name])
            
            self.save_data()

    def rename_category_from_context(self, item):
        """从右键菜单重命名"""
        old_name = item.text(0)
        new_name, ok = QInputDialog.getText(self, "重命名", "请输入新名称:", text=old_name)
        if ok and new_name and new_name != old_name:
            try:
                parent_path = self.get_item_path(item.parent())
                if parent_path:
                    # 使用 get_parent_data_by_path 获取父级的 children 字典
                    parent_data = self.get_parent_data_by_path(parent_path + [old_name])
                    if parent_data and old_name in parent_data:
                        parent_data[new_name] = parent_data.pop(old_name)
                else:
                    if old_name in self.system_data["categories"]:
                        self.system_data["categories"][new_name] = self.system_data["categories"].pop(old_name)
                
                # 记住当前展开状态
                expanded_items = self.get_expanded_items()
                
                # 重新构建树
                self.init_tree()
                
                # 恢复展开状态
                self.restore_expanded_items(expanded_items)
                
                self.save_data()
                QMessageBox.information(self, "成功", f"'{old_name}' 已重命名为 '{new_name}'！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重命名失败: {str(e)}")

    def delete_category_from_context(self, item):
        """从右键菜单删除"""
        name = item.text(0)
        reply = QMessageBox.question(self, "确认删除", f"确定要删除 '{name}' 吗？")
        if reply == QMessageBox.Yes:
            try:
                parent_path = self.get_item_path(item.parent())
                if parent_path:
                    # 使用 get_parent_data_by_path 获取父级的 children 字典
                    parent_data = self.get_parent_data_by_path(parent_path + [name])
                    if parent_data and name in parent_data:
                        del parent_data[name]
                else:
                    if name in self.system_data["categories"]:
                        del self.system_data["categories"][name]
                
                # 记住当前展开状态
                expanded_items = self.get_expanded_items()
                
                # 重新构建树
                self.init_tree()
                
                # 恢复展开状态
                self.restore_expanded_items(expanded_items)
                
                self.save_data()
                QMessageBox.information(self, "成功", f"'{name}' 已删除！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")

    def search_by_price_range(self):
        """根据价格区间搜索当前产品的供应商"""
        try:
            print("=== 开始当前产品价格搜索 ===")
            
            # 检查是否选择了产品
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个产品！")
                return
            
            # 检查UI元素是否存在
            if not hasattr(self, 'min_price_edit') or not hasattr(self, 'max_price_edit'):
                error_msg = "价格搜索UI元素未初始化"
                print(error_msg)
                QMessageBox.critical(self, "搜索失败", error_msg)
                return
            
            # 获取当前产品数据
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取产品路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到产品数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "只能搜索具体产品的供应商信息！")
                return
            
            print(f"获取到产品数据: {data}")
            print(f"产品数据键: {list(data.keys())}")
            if "pricing" in data:
                print(f"价格信息: {data['pricing']}")
            else:
                print("产品没有价格信息")
            
            min_price_text = self.min_price_edit.text().strip()
            max_price_text = self.max_price_edit.text().strip()
            
            print(f"开始价格搜索 - 产品: {' > '.join(path)} - 最低价: '{min_price_text}', 最高价: '{max_price_text}'")
            
            if not min_price_text and not max_price_text:
                QMessageBox.warning(self, "警告", "请输入至少一个价格范围！")
                return
            
            # 解析价格范围
            min_price = None
            max_price = None
            
            if min_price_text:
                try:
                    min_price = float(min_price_text)
                    print(f"解析最低价格: {min_price}")
                except ValueError:
                    QMessageBox.warning(self, "警告", "最低价格格式不正确！")
                    return
            
            if max_price_text:
                try:
                    max_price = float(max_price_text)
                    print(f"解析最高价格: {max_price}")
                except ValueError:
                    QMessageBox.warning(self, "警告", "最高价格格式不正确！")
                    return
            
            # 检查价格范围逻辑
            if min_price is not None and max_price is not None and min_price > max_price:
                QMessageBox.warning(self, "警告", "最低价格不能大于最高价格！")
                return
            
            print(f"价格范围验证通过 - 搜索范围: {min_price} 到 {max_price}")
            
            # 搜索当前产品的供应商
            results = []
            self.search_current_product_suppliers(data, path, min_price, max_price, results)
            
            # 存储搜索结果数据以便后续访问
            self.current_price_search_results = results.copy() if results else []
            
            print(f"搜索完成，找到 {len(results)} 条结果")
            
            # 检查结果表格是否存在
            if not hasattr(self, 'price_search_results'):
                error_msg = "价格搜索结果表格未初始化"
                print(error_msg)
                QMessageBox.critical(self, "搜索失败", error_msg)
                return
            
            # 显示结果
            self.price_search_results.clear()
            self.price_search_results.setRowCount(len(results))
            
            # 重新设置表格标题，确保显示正确的标题
            headers = ["型号", "供应商", "价格", "供货周期", "联系方式", "产品图片"]
            self.price_search_results.setHorizontalHeaderLabels(headers)
            
            # 确保表头可见并刷新
            self.price_search_results.horizontalHeader().setVisible(True)
            self.price_search_results.horizontalHeader().setStretchLastSection(True)
            print(f"价格搜索结果表格当前标题: {[self.price_search_results.horizontalHeaderItem(i).text() if self.price_search_results.horizontalHeaderItem(i) else f'列{i}' for i in range(self.price_search_results.columnCount())]}")
            
            for row, result in enumerate(results):
                try:
                    # 设置表格数据
                    self.price_search_results.setItem(row, 0, QTableWidgetItem(result['model']))
                    self.price_search_results.setItem(row, 1, QTableWidgetItem(result['supplier_name']))
                    self.price_search_results.setItem(row, 2, QTableWidgetItem(str(result['supplier_price'])))
                    self.price_search_results.setItem(row, 3, QTableWidgetItem(result['lead_time']))
                    self.price_search_results.setItem(row, 4, QTableWidgetItem(result['contact']))
                    
                    # 添加产品图片信息 - 使用缩略图组件
                    product_images = result.get('product_images', [])
                    print(f"搜索结果行 {row}: 产品图片数量: {len(product_images)}, 图片列表: {product_images}")
                    print(f"图片目录路径: {self.images_dir}")
                    image_widget = PriceSearchImageWidget(product_images, self.images_dir, self.price_search_results)
                    self.price_search_results.setCellWidget(row, 5, image_widget)
                    
                    print(f"添加结果行 {row}: {result['supplier_name']} - {result['supplier_price']} - 产品图片: {len(product_images)}张")
                except Exception as row_error:
                    print(f"添加结果行 {row} 时出错: {row_error}")
                    continue
            
            # 强制刷新表格显示
            self.price_search_results.resizeColumnsToContents()
            # 调整行高以显示缩略图
            self.price_search_results.resizeRowsToContents()
            # 确保所有行都有足够的高度显示缩略图
            for row in range(len(results)):
                self.price_search_results.setRowHeight(row, max(60, self.price_search_results.rowHeight(row)))
            self.price_search_results.update()
            
            # 显示搜索结果数量
            if results:
                result_msg = f"找到 {len(results)} 条供应商信息"
                self.price_search_results.setToolTip(result_msg)
                # 重置排序按钮状态
                self.price_sort_btn.setText("按价格升序")
                self.price_sort_desc_btn.setText("按价格降序")
                # 在状态栏显示搜索结果
                self.statusBar().showMessage(result_msg, 3000)
            else:
                # 重置排序按钮状态
                self.price_sort_btn.setText("按价格升序")
                self.price_sort_desc_btn.setText("按价格降序")
                # 在状态栏显示搜索结果
                self.statusBar().showMessage("未找到符合条件的供应商信息", 3000)
        except Exception as e:
            error_msg = f"价格搜索失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "搜索失败", error_msg)
    
    def search_current_product_suppliers(self, data, path, min_price, max_price, results):
        """搜索当前产品的供应商信息"""
        try:
            print(f"搜索产品: {' > '.join(path)}")
            
            # 检查产品是否有价格信息
            if "pricing" not in data:
                print("  产品没有价格信息")
                return
            
            pricing = data["pricing"]
            
            # 获取型号信息
            model_info = ""
            if "technical_params" in data and "型号" in data["technical_params"]:
                model_info = data["technical_params"]["型号"]
            elif "technical_params" in data:
                # 如果没有"型号"字段，尝试获取第一个技术参数作为型号
                tech_params = data["technical_params"]
                if tech_params:
                    first_param = list(tech_params.items())[0]
                    model_info = f"{first_param[0]}: {first_param[1]}"
            
            # 获取供应商信息
            suppliers = pricing.get("suppliers", [])
            print(f"  供应商数量: {len(suppliers)}")
            
            if not suppliers:
                print("  没有供应商信息，跳过")
                return
            
            # 搜索供应商
            for supplier in suppliers:
                # 检查供应商是否有价格信息
                if 'price' not in supplier or supplier['price'] is None or supplier['price'] == '':
                    print(f"  供应商 {supplier.get('name', '未知')} 没有价格信息，跳过")
                    continue
                
                # 转换供应商价格为浮点数
                try:
                    supplier_price = float(supplier['price'])
                    print(f"  检查供应商: {supplier.get('name', '未知')} - 价格: {supplier_price} (类型: {type(supplier_price)})")
                except (ValueError, TypeError):
                    print(f"  供应商价格转换失败: {supplier['price']}")
                    continue
                
                if self.is_price_in_range(supplier_price, min_price, max_price):
                    # 获取供应商特定的产品图片信息
                    product_images = supplier.get('images', [])
                    
                    result = {
                        'path': path,
                        'model': model_info,
                        'supplier_name': supplier.get('name', '未知供应商'),
                        'supplier_price': supplier_price,
                        'lead_time': supplier.get('lead_time', ''),
                        'contact': supplier.get('contact', ''),
                        'product_images': product_images
                    }
                    results.append(result)
                    print(f"  添加供应商结果: {result['supplier_name']} - {result['supplier_price']} - 产品图片: {len(product_images)}张")
                else:
                    print(f"  供应商价格 {supplier_price} 不在范围内，跳过")
                    
        except Exception as e:
            print(f"搜索当前产品供应商时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def is_price_in_range(self, price, min_price, max_price):
        """检查价格是否在指定范围内"""
        print(f"检查价格范围: 价格={price}, 最低价={min_price}, 最高价={max_price}")
        if min_price is not None and price < min_price:
            print(f"  价格 {price} 低于最低价 {min_price}，返回 False")
            return False
        if max_price is not None and price > max_price:
            print(f"  价格 {price} 高于最高价 {max_price}，返回 False")
            return False
        print(f"  价格 {price} 在范围内，返回 True")
        return True

    def search_products_by_price(self, data, current_path, min_price, max_price, results):
        """递归搜索产品价格"""
        try:
            if not isinstance(data, dict):
                print(f"警告: 数据不是字典类型: {type(data)}")
                return
                
            for name, info in data.items():
                try:
                    path = current_path + [name]
                    
                    if isinstance(info, dict) and "children" in info:
                        # 这是一个分类节点，继续递归
                        print(f"进入分类: {' > '.join(path)}")
                        self.search_products_by_price(info["children"], path, min_price, max_price, results)
                    else:
                        # 这是一个产品节点，检查供应商价格
                        print(f"检查产品: {' > '.join(path)}")
                        if "pricing" in info and "suppliers" in info["pricing"]:
                            suppliers = info["pricing"]["suppliers"]
                            print(f"  供应商数量: {len(suppliers)}")
                            
                            # 只处理有供应商信息的产品
                            if not suppliers:
                                print(f"  产品没有供应商信息，跳过")
                                continue
                            
                            # 获取型号信息
                            model_info = ""
                            if "technical_params" in info and "型号" in info["technical_params"]:
                                model_info = info["technical_params"]["型号"]
                            elif "technical_params" in info:
                                # 如果没有"型号"字段，尝试获取第一个技术参数作为型号
                                tech_params = info["technical_params"]
                                if tech_params:
                                    first_param = list(tech_params.items())[0]
                                    model_info = f"{first_param[0]}: {first_param[1]}"
                            
                            # 只处理有供应商信息的产品
                            if suppliers:
                                # 为每个有价格的供应商创建一个条目
                                for supplier in suppliers:
                                    # 检查供应商是否有价格信息
                                    if 'price' not in supplier or supplier['price'] is None or supplier['price'] == '':
                                        print(f"  供应商 {supplier.get('name', '未知')} 没有价格信息，跳过")
                                        continue
                                    
                                    try:
                                        supplier_price = float(supplier['price'])
                                    except (ValueError, TypeError):
                                        print(f"  供应商价格转换失败: {supplier['price']}")
                                        continue
                                    
                                    # 检查供应商价格是否在范围内
                                    if min_price is not None and supplier_price < min_price:
                                        print(f"  供应商价格 {supplier_price} 低于最低价 {min_price}，跳过")
                                        continue
                                    if max_price is not None and supplier_price > max_price:
                                        print(f"  供应商价格 {supplier_price} 高于最高价 {max_price}，跳过")
                                        continue
                                    
                                    # 获取产品图片信息
                                    product_images = info.get('images', [])
                                    
                                    result = {
                                        'path': path,
                                        'model': model_info,
                                        'supplier_name': supplier.get('name', '未知供应商'),
                                        'supplier_price': supplier_price,
                                        'lead_time': supplier.get('lead_time', ''),
                                        'contact': supplier.get('contact', ''),
                                        'product_images': product_images
                                    }
                                    results.append(result)
                                    print(f"  添加供应商结果: {result['supplier_name']} - {result['supplier_price']} - 产品图片: {len(product_images)}张")
                            else:
                                print(f"  产品没有供应商信息，跳过")
                        else:
                            print(f"  产品没有价格信息")
                except Exception as item_error:
                    print(f"处理项目 '{name}' 时出错: {item_error}")
                    continue
                    
        except Exception as e:
            print(f"递归搜索过程中出错: {e}")
            import traceback
            traceback.print_exc()

    def debug_current_product(self):
        """调试当前产品信息"""
        try:
            print("=== 开始调试当前产品 ===")
            
            if not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个产品！")
                return
            
            path = self.get_item_path(self.current_item)
            if not path:
                QMessageBox.warning(self, "警告", "无法获取产品路径！")
                return
                
            data = self.get_data_by_path(path)
            if not data:
                QMessageBox.warning(self, "警告", "无法找到产品数据！")
                return
                
            if "children" in data:
                QMessageBox.warning(self, "警告", "请选择具体产品，不是分类！")
                return
            
            print(f"当前产品路径: {' > '.join(path)}")
            print(f"产品数据键: {list(data.keys())}")
            print(f"完整产品数据: {data}")
            
            if "pricing" in data:
                pricing = data["pricing"]
                print(f"价格信息: {pricing}")
                
                if "base_price" in pricing:
                    base_price = pricing["base_price"]
                    print(f"基础价格: {base_price} (类型: {type(base_price)})")
                    try:
                        base_price_float = float(base_price)
                        print(f"基础价格转换为浮点数: {base_price_float}")
                    except (ValueError, TypeError) as e:
                        print(f"基础价格转换失败: {e}")
                else:
                    print("没有基础价格")
                
                if "suppliers" in pricing:
                    suppliers = pricing["suppliers"]
                    print(f"供应商数量: {len(suppliers)}")
                    for i, supplier in enumerate(suppliers):
                        print(f"  供应商{i+1}: {supplier}")
                        if "price" in supplier:
                            try:
                                price_float = float(supplier["price"])
                                print(f"    价格转换为浮点数: {price_float}")
                            except (ValueError, TypeError) as e:
                                print(f"    价格转换失败: {e}")
                else:
                    print("没有供应商信息")
            else:
                print("产品没有价格信息")
            
            # 显示调试信息给用户
            debug_info = f"产品路径: {' > '.join(path)}\n"
            debug_info += f"数据键: {list(data.keys())}\n"
            
            if "pricing" in data:
                pricing = data["pricing"]
                debug_info += f"有价格信息\n"
                if "base_price" in pricing:
                    debug_info += f"基础价格: {pricing['base_price']}\n"
                if "suppliers" in pricing:
                    suppliers = pricing["suppliers"]
                    debug_info += f"供应商数量: {len(suppliers)}\n"
                    for i, supplier in enumerate(suppliers):
                        debug_info += f"  供应商{i+1}: {supplier.get('name', '未知')} - {supplier.get('price', '未知价格')}\n"
            else:
                debug_info += "没有价格信息\n"
            
            QMessageBox.information(self, "当前产品调试信息", debug_info)
            
        except Exception as e:
            error_msg = f"调试当前产品失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "调试失败", error_msg)

    def test_price_search(self):
        """测试价格搜索功能"""
        try:
            print("=== 开始测试价格搜索功能 ===")
            
            # 检查系统数据
            if not hasattr(self, 'system_data'):
                error_msg = "系统数据未初始化"
                print(error_msg)
                QMessageBox.critical(self, "测试失败", error_msg)
                return
                
            print(f"系统数据键: {list(self.system_data.keys())}")
            
            if "categories" not in self.system_data:
                error_msg = "系统数据中缺少categories字段"
                print(error_msg)
                QMessageBox.critical(self, "测试失败", error_msg)
                return
                
            categories = self.system_data.get('categories', {})
            print(f"分类数据键: {list(categories.keys())}")
            
            # 统计所有产品数量
            total_products = 0
            products_with_pricing = 0
            products_with_suppliers = 0
            
            def count_products(data, path=[]):
                nonlocal total_products, products_with_pricing, products_with_suppliers
                try:
                    for name, info in data.items():
                        current_path = path + [name]
                        if isinstance(info, dict) and "children" in info:
                            count_products(info["children"], current_path)
                        else:
                            total_products += 1
                            print(f"检查产品: {' > '.join(current_path)}")
                            
                            if "pricing" in info:
                                print(f"  有pricing字段")
                                if "base_price" in info["pricing"]:
                                    products_with_pricing += 1
                                    price = info["pricing"]["base_price"]
                                    print(f"  找到有价格的产品: {' > '.join(current_path)} - 价格: {price}")
                                    
                                    # 检查供应商信息
                                    if "suppliers" in info["pricing"] and info["pricing"]["suppliers"]:
                                        suppliers = info["pricing"]["suppliers"]
                                        products_with_suppliers += 1
                                        print(f"  供应商数量: {len(suppliers)}")
                                        for i, supplier in enumerate(suppliers):
                                            print(f"    供应商{i+1}: {supplier.get('name', '未知')} - {supplier.get('price', '未知价格')}")
                                    else:
                                        print(f"  没有供应商信息")
                                else:
                                    print(f"  有pricing字段但没有base_price")
                            else:
                                print(f"  没有pricing字段")
                except Exception as e:
                    print(f"统计产品时出错: {e}")
            
            count_products(categories)
            
            result_msg = f"系统统计:\n总产品数: {total_products}\n有价格信息的产品: {products_with_pricing}\n有供应商信息的产品: {products_with_suppliers}"
            print(result_msg)
            QMessageBox.information(self, "价格搜索测试", result_msg)
            
        except Exception as e:
            error_msg = f"测试价格搜索失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "测试失败", error_msg)

    def select_price_search_result(self, item):
        """选择价格搜索结果"""
        try:
            # 获取选中的行
            row = item.row()
            if row >= 0:
                # 获取供应商信息（注意列索引已调整）
                supplier_item = self.price_search_results.item(row, 1)  # 供应商列
                price_item = self.price_search_results.item(row, 2)     # 价格列
                images_item = self.price_search_results.item(row, 5)    # 产品图片列
                
                if supplier_item and price_item:
                    supplier_name = supplier_item.text()
                    price = price_item.text()
                    images_text = images_item.text() if images_item else "无图片"
                    
                    # 检查是否点击的是图片列
                    if item.column() == 5 and images_text != "无图片":
                        # 尝试获取产品图片路径并显示
                        try:
                            print(f"=== 處理圖片列雙擊 ===")
                            print(f"行: {row}, 供應商: {supplier_name}, 價格: {price}")
                            print(f"圖片文本: {images_text}")
                            
                            # 从存储的搜索结果中获取图片数据
                            if hasattr(self, 'current_price_search_results') and row < len(self.current_price_search_results):
                                result_data = self.current_price_search_results[row]
                                product_images = result_data.get('product_images', [])
                                print(f"從搜索結果獲取的圖片數據: {product_images}")
                                print(f"圖片數量: {len(product_images)}")
                                
                                if product_images:
                                    # 构建完整的图片路径列表
                                    image_paths = []
                                    missing_images = []
                                    for img_filename in product_images:
                                        img_path = os.path.join(self.images_dir, img_filename)
                                        if os.path.exists(img_path):
                                            image_paths.append(img_path)
                                        else:
                                            missing_images.append(img_filename)
                                    
                                    if image_paths:
                                        # 显示图片查看器
                                        dialog = ImageViewerDialog(image_paths, 0, self)
                                        dialog.exec_()
                                    else:
                                        if missing_images:
                                            QMessageBox.information(self, "产品图片", 
                                                                  f"图片文件不存在:\n{', '.join(missing_images[:3])}\n供应商: {supplier_name}\n价格: {price}")
                                        else:
                                            QMessageBox.information(self, "产品图片", 
                                                                  f"该产品没有图片\n供应商: {supplier_name}\n价格: {price}")
                                else:
                                    QMessageBox.information(self, "产品图片", 
                                                          f"该产品没有图片\n供应商: {supplier_name}\n价格: {price}")
                            else:
                                QMessageBox.information(self, "产品图片", 
                                                      f"无法获取图片数据\n供应商: {supplier_name}\n价格: {price}")
                        except Exception as img_error:
                            print(f"显示产品图片失败: {img_error}")
                            QMessageBox.information(self, "供应商信息", 
                                                  f"显示图片时出错\n供应商: {supplier_name}\n价格: {price}\n错误: {str(img_error)}")
                    else:
                        # 显示选中信息
                        info_msg = f"已选择供应商: {supplier_name}\n价格: {price}\n图片信息: {images_text}"
                        QMessageBox.information(self, "供应商信息", info_msg)
                    
                    # 切换到价格管理标签页
                    self.tab_widget.setCurrentIndex(2)  # 价格管理是第3个标签页（索引2）
            
        except Exception as e:
            error_msg = f"选择价格搜索结果失败: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "选择失败", error_msg)
    
    def sort_price_results_ascending(self):
        """按价格升序排序搜索结果"""
        try:
            self.sort_price_results(ascending=True)
        except Exception as e:
            print(f"价格升序排序失败: {e}")
            QMessageBox.critical(self, "排序失败", f"价格升序排序失败: {str(e)}")
    
    def sort_price_results_descending(self):
        """按价格降序排序搜索结果"""
        try:
            self.sort_price_results(ascending=False)
        except Exception as e:
            print(f"价格降序排序失败: {e}")
            QMessageBox.critical(self, "排序失败", f"价格降序排序失败: {str(e)}")
    
    def sort_price_results(self, ascending=True):
        """排序价格搜索结果"""
        try:
            if not hasattr(self, 'price_search_results'):
                QMessageBox.warning(self, "警告", "搜索结果表格不存在！")
                return
            
            # 获取当前表格数据
            rows = self.price_search_results.rowCount()
            if rows == 0:
                QMessageBox.information(self, "提示", "没有搜索结果可排序！")
                return
            
            # 收集所有行数据
            table_data = []
            for row in range(rows):
                row_data = []
                for col in range(self.price_search_results.columnCount()):
                    item = self.price_search_results.item(row, col)
                    row_data.append(item.text() if item else "")
                table_data.append(row_data)
            
            # 按价格列（第3列，索引2）排序
            try:
                table_data.sort(key=lambda x: float(x[2]) if x[2] and x[2].replace('.', '').replace('-', '').isdigit() else float('inf'), reverse=not ascending)
            except (ValueError, IndexError):
                QMessageBox.warning(self, "警告", "价格数据格式错误，无法排序！")
                return
            
            # 重新填充表格
            self.price_search_results.clearContents()
            self.price_search_results.setRowCount(len(table_data))
            
            for row, row_data in enumerate(table_data):
                for col, cell_data in enumerate(row_data):
                    self.price_search_results.setItem(row, col, QTableWidgetItem(cell_data))
            
            # 更新排序按钮文本
            if ascending:
                self.price_sort_btn.setText("按价格升序 ✓")
                self.price_sort_desc_btn.setText("按价格降序")
            else:
                self.price_sort_btn.setText("按价格升序")
                self.price_sort_desc_btn.setText("按价格降序 ✓")
            
            # 在状态栏显示排序完成信息，而不是弹出消息框
            self.statusBar().showMessage(f"已按价格{'升序' if ascending else '降序'}排序完成", 3000)
            
        except Exception as e:
            print(f"排序价格搜索结果时出错: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "排序失败", f"排序价格搜索结果时出错: {str(e)}")
            
    def create_basic_tab(self):
        """创建基本信息标签页"""
        layout = QVBoxLayout()
        
        # 内容编辑区
        content_label = QLabel("设备描述:")
        self.content_edit = QTextEdit()
        self.content_edit.textChanged.connect(self.auto_save_content)
        layout.addWidget(content_label)
        layout.addWidget(self.content_edit)
        
        # 标签编辑区
        tags_label = QLabel("标签:")
        self.tags_edit = QLineEdit()
        self.tags_edit.textChanged.connect(self.auto_save_tags)
        layout.addWidget(tags_label)
        layout.addWidget(self.tags_edit)
        
        # 图片管理区域
        images_label = QLabel("设备图片:")
        layout.addWidget(images_label)
        
        # 图片缩略图区域
        self.images_scroll = QScrollArea()
        self.images_widget = QWidget()
        self.images_layout = QHBoxLayout()
        
        # 添加图片提示标签
        self.image_thumbnail_label = QLabel("暂无图片")
        self.image_thumbnail_label.setAlignment(Qt.AlignCenter)
        self.image_thumbnail_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
        self.image_thumbnail_label.setMinimumHeight(80)
        
        # 先添加弹性空间，再添加标签，确保标签居中
        self.images_layout.addStretch()
        self.images_layout.addWidget(self.image_thumbnail_label)
        self.images_layout.addStretch()
        
        self.images_widget.setLayout(self.images_layout)
        self.images_scroll.setWidget(self.images_widget)
        self.images_scroll.setWidgetResizable(True)
        self.images_scroll.setMaximumHeight(120)
        layout.addWidget(self.images_scroll)
        
        # 图片操作按钮
        images_btn_layout = QHBoxLayout()
        self.insert_image_btn = QPushButton("插入图片")
        self.insert_image_btn.clicked.connect(self.insert_image)
        self.save_image_btn = QPushButton("保存图片")
        self.save_image_btn.clicked.connect(self.save_image)
        self.manage_images_btn = QPushButton("管理图片")
        self.manage_images_btn.clicked.connect(self.manage_images)
        
        images_btn_layout.addWidget(self.insert_image_btn)
        images_btn_layout.addWidget(self.save_image_btn)
        images_btn_layout.addWidget(self.manage_images_btn)
        layout.addLayout(images_btn_layout)
        
        # 原理图片管理区域
        principle_images_label = QLabel("原理图片:")
        layout.addWidget(principle_images_label)
        
        # 原理图片缩略图区域
        self.principle_images_scroll = QScrollArea()
        self.principle_images_widget = QWidget()
        self.principle_images_layout = QHBoxLayout()
        
        # 添加原理图片提示标签
        self.principle_image_thumbnail_label = QLabel("暂无原理图片")
        self.principle_image_thumbnail_label.setAlignment(Qt.AlignCenter)
        self.principle_image_thumbnail_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
        self.principle_image_thumbnail_label.setMinimumHeight(80)
        
        # 先添加弹性空间，再添加标签，确保标签居中
        self.principle_images_layout.addStretch()
        self.principle_images_layout.addWidget(self.principle_image_thumbnail_label)
        self.principle_images_layout.addStretch()
        
        self.principle_images_widget.setLayout(self.principle_images_layout)
        self.principle_images_scroll.setWidget(self.principle_images_widget)
        self.principle_images_scroll.setWidgetResizable(True)
        self.principle_images_scroll.setMaximumHeight(120)
        layout.addWidget(self.principle_images_scroll)
        
        # 原理图片操作按钮
        principle_images_btn_layout = QHBoxLayout()
        self.insert_principle_image_btn = QPushButton("插入原理图片")
        self.insert_principle_image_btn.clicked.connect(self.insert_principle_image)
        self.save_principle_image_btn = QPushButton("保存原理图片")
        self.save_principle_image_btn.clicked.connect(self.save_principle_image)
        self.manage_principle_images_btn = QPushButton("管理原理图片")
        self.manage_principle_images_btn.clicked.connect(self.manage_principle_images)
        
        principle_images_btn_layout.addWidget(self.insert_principle_image_btn)
        principle_images_btn_layout.addWidget(self.save_principle_image_btn)
        principle_images_btn_layout.addWidget(self.manage_principle_images_btn)
        layout.addLayout(principle_images_btn_layout)
        
        self.basic_tab.setLayout(layout)
    
    def create_tech_tab(self):
        """创建技术参数标签页"""
        layout = QVBoxLayout()
        
        # 技术参数表格
        self.tech_table = QTableWidget()
        self.tech_table.setColumnCount(2)
        self.tech_table.setHorizontalHeaderLabels(["参数名称", "参数值"])
        layout.addWidget(self.tech_table)
        
        # 技术参数操作按钮
        tech_btn_layout = QHBoxLayout()
        self.add_tech_param_btn = QPushButton("添加参数")
        self.add_tech_param_btn.clicked.connect(self.add_tech_param)
        self.del_tech_param_btn = QPushButton("删除参数")
        self.del_tech_param_btn.clicked.connect(self.del_tech_param)
        self.save_tech_params_btn = QPushButton("保存参数")
        self.save_tech_params_btn.clicked.connect(self.save_tech_params)
        
        tech_btn_layout.addWidget(self.add_tech_param_btn)
        tech_btn_layout.addWidget(self.del_tech_param_btn)
        tech_btn_layout.addWidget(self.save_tech_params_btn)
        layout.addLayout(tech_btn_layout)
        
        self.tech_tab.setLayout(layout)
    
    def create_price_tab(self):
        """创建价格管理标签页"""
        layout = QVBoxLayout()
        
        # 基础价格设置
        base_price_layout = QHBoxLayout()
        base_price_label = QLabel("基础价格:")
        self.base_price_edit = QLineEdit()
        self.base_price_edit.textChanged.connect(self.auto_save_pricing)
        currency_label = QLabel("货币:")
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["CNY", "USD", "EUR"])
        self.currency_combo.currentTextChanged.connect(self.auto_save_pricing)
        
        base_price_layout.addWidget(base_price_label)
        base_price_layout.addWidget(self.base_price_edit)
        base_price_layout.addWidget(currency_label)
        base_price_layout.addWidget(self.currency_combo)
        layout.addLayout(base_price_layout)
        
        # 供应商管理
        supplier_label = QLabel("供应商信息:")
        layout.addWidget(supplier_label)
        
        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(6)
        self.supplier_table.setHorizontalHeaderLabels(["型号", "供应商", "价格", "供货周期", "联系方式", "产品图片"])
        self.supplier_table.setColumnWidth(4, 200)  # 联系方式列宽
        self.supplier_table.doubleClicked.connect(self.on_supplier_table_double_clicked)
        layout.addWidget(self.supplier_table)
        
        # 供应商操作按钮
        supplier_btn_layout = QHBoxLayout()
        self.add_supplier_btn = QPushButton("添加供应商")
        self.add_supplier_btn.clicked.connect(self.add_supplier)
        self.del_supplier_btn = QPushButton("删除供应商")
        self.del_supplier_btn.clicked.connect(self.del_supplier)
        self.save_pricing_btn = QPushButton("保存价格信息")
        self.save_pricing_btn.clicked.connect(self.save_pricing)
        
        supplier_btn_layout.addWidget(self.add_supplier_btn)
        supplier_btn_layout.addWidget(self.del_supplier_btn)
        supplier_btn_layout.addWidget(self.save_pricing_btn)
        layout.addLayout(supplier_btn_layout)
        
        # 价格搜索区域
        search_label = QLabel("价格搜索:")
        layout.addWidget(search_label)
        
        search_layout = QHBoxLayout()
        min_price_label = QLabel("最低价格:")
        self.min_price_edit = QLineEdit()
        max_price_label = QLabel("最高价格:")
        self.max_price_edit = QLineEdit()
        self.search_price_btn = QPushButton("搜索")
        self.search_price_btn.clicked.connect(self.search_by_price_range)
        
        search_layout.addWidget(min_price_label)
        search_layout.addWidget(self.min_price_edit)
        search_layout.addWidget(max_price_label)
        search_layout.addWidget(self.max_price_edit)
        search_layout.addWidget(self.search_price_btn)
        layout.addLayout(search_layout)
        
        # 价格搜索结果
        results_label = QLabel("搜索结果:")
        layout.addWidget(results_label)
        
        self.price_search_results = QTableWidget()
        self.price_search_results.setColumnCount(6)
        self.price_search_results.setHorizontalHeaderLabels(["型号", "供应商", "价格", "供货周期", "联系方式", "产品图片"])
        self.price_search_results.setColumnWidth(4, 200)  # 联系方式列宽
        self.price_search_results.setColumnWidth(5, 160)  # 产品图片列宽
        self.price_search_results.verticalHeader().setDefaultSectionSize(60)  # 设置默认行高
        self.price_search_results.doubleClicked.connect(self.select_price_search_result)
        layout.addWidget(self.price_search_results)
        
        # 搜索结果操作按钮
        results_btn_layout = QHBoxLayout()
        self.price_sort_btn = QPushButton("按价格升序")
        self.price_sort_btn.clicked.connect(self.sort_price_results_ascending)
        self.price_sort_desc_btn = QPushButton("按价格降序")
        self.price_sort_desc_btn.clicked.connect(self.sort_price_results_descending)
        
        results_btn_layout.addWidget(self.price_sort_btn)
        results_btn_layout.addWidget(self.price_sort_desc_btn)
        layout.addLayout(results_btn_layout)
        
        self.price_tab.setLayout(layout)
    
    def create_maintenance_tab(self):
        """创建维护保养标签页"""
        layout = QVBoxLayout()
        
        # 维护周期
        cycle_label = QLabel("维护周期:")
        self.cycle_edit = QLineEdit()
        self.cycle_edit.textChanged.connect(self.auto_save_maintenance)
        layout.addWidget(cycle_label)
        layout.addWidget(self.cycle_edit)
        
        # 维护程序
        procedures_label = QLabel("维护程序:")
        self.procedures_edit = QTextEdit()
        self.procedures_edit.textChanged.connect(self.auto_save_maintenance)
        layout.addWidget(procedures_label)
        layout.addWidget(self.procedures_edit)
        
        # 注意事项
        notes_label = QLabel("注意事项:")
        self.notes_edit = QTextEdit()
        self.notes_edit.textChanged.connect(self.auto_save_maintenance)
        layout.addWidget(notes_label)
        layout.addWidget(self.notes_edit)
        
        # 保存按钮
        self.save_maintenance_btn = QPushButton("保存维护信息")
        self.save_maintenance_btn.clicked.connect(self.save_maintenance)
        layout.addWidget(self.save_maintenance_btn)
        
        self.maintenance_tab.setLayout(layout)
    
    def create_parts_tab(self):
        """创建零部件附页标签页"""
        layout = QVBoxLayout()
        
        # 左侧：零部件列表
        left_parts_layout = QVBoxLayout()
        parts_list_label = QLabel("零部件列表:")
        left_parts_layout.addWidget(parts_list_label)
        
        self.parts_list = QListWidget()
        self.parts_list.itemClicked.connect(self.load_part_details)
        self.parts_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parts_list.customContextMenuRequested.connect(self.show_parts_context_menu)
        left_parts_layout.addWidget(self.parts_list)
        
        # 零部件操作按钮
        parts_btn_layout = QHBoxLayout()
        self.add_part_btn = QPushButton("添加零部件")
        self.add_part_btn.clicked.connect(self.add_part)
        self.del_part_btn = QPushButton("删除零部件")
        self.del_part_btn.clicked.connect(self.delete_part)
        
        parts_btn_layout.addWidget(self.add_part_btn)
        parts_btn_layout.addWidget(self.del_part_btn)
        left_parts_layout.addLayout(parts_btn_layout)
        
        # 右侧：零部件详情
        right_parts_layout = QVBoxLayout()
        part_details_label = QLabel("零部件详情:")
        right_parts_layout.addWidget(part_details_label)
        
        # 零部件名称
        part_name_label = QLabel("名称:")
        self.part_name_edit = QLineEdit()
        right_parts_layout.addWidget(part_name_label)
        right_parts_layout.addWidget(self.part_name_edit)
        
        # 零部件描述
        part_description_label = QLabel("描述:")
        self.part_description = QTextEdit()
        right_parts_layout.addWidget(part_description_label)
        right_parts_layout.addWidget(self.part_description)
        
        # 零部件原理图片
        part_principle_images_label = QLabel("原理图片:")
        right_parts_layout.addWidget(part_principle_images_label)
        
        # 原理图片缩略图区域
        self.part_principle_images_scroll = QScrollArea()
        self.part_principle_images_widget = QWidget()
        self.part_principle_images_layout = QHBoxLayout()
        self.part_principle_images_layout.addStretch()
        self.part_principle_images_widget.setLayout(self.part_principle_images_layout)
        self.part_principle_images_scroll.setWidget(self.part_principle_images_widget)
        self.part_principle_images_scroll.setWidgetResizable(True)
        self.part_principle_images_scroll.setMaximumHeight(120)
        right_parts_layout.addWidget(self.part_principle_images_scroll)
        
        # 原理图片操作按钮
        part_principle_images_btn_layout = QHBoxLayout()
        self.insert_part_principle_image_btn = QPushButton("插入原理图片")
        self.insert_part_principle_image_btn.clicked.connect(self.insert_part_principle_image)
        self.save_part_principle_image_btn = QPushButton("保存原理图片")
        self.save_part_principle_image_btn.clicked.connect(self.save_part_principle_image)
        self.manage_part_principle_images_btn = QPushButton("管理原理图片")
        self.manage_part_principle_images_btn.clicked.connect(self.manage_part_principle_images)
        
        part_principle_images_btn_layout.addWidget(self.insert_part_principle_image_btn)
        part_principle_images_btn_layout.addWidget(self.save_part_principle_image_btn)
        part_principle_images_btn_layout.addWidget(self.manage_part_principle_images_btn)
        right_parts_layout.addLayout(part_principle_images_btn_layout)
        
        # 组合左右布局
        parts_main_layout = QHBoxLayout()
        left_parts_widget = QWidget()
        left_parts_widget.setLayout(left_parts_layout)
        left_parts_widget.setMaximumWidth(300)
        parts_main_layout.addWidget(left_parts_widget)
        
        right_parts_widget = QWidget()
        right_parts_widget.setLayout(right_parts_layout)
        parts_main_layout.addWidget(right_parts_widget)
        
        layout.addLayout(parts_main_layout)
        self.parts_tab.setLayout(layout)
    
    def show_parts_context_menu(self, position):
        """显示零部件列表右键菜单"""
        try:
            item = self.parts_list.itemAt(position)
            if not item:
                return
            
            menu = QMenu(self)
            
            # 删除零部件选项
            delete_action = menu.addAction("删除零部件")
            delete_action.triggered.connect(lambda: self.delete_part_from_context(item))
            
            # 重命名零部件选项
            rename_action = menu.addAction("重命名零部件")
            rename_action.triggered.connect(lambda: self.rename_part_from_context(item))
            
            # 显示菜单
            menu.exec_(self.parts_list.mapToGlobal(position))
            
        except Exception as e:
            print(f"显示零部件右键菜单失败: {e}")
    
    def delete_part_from_context(self, item):
        """从右键菜单删除零部件"""
        try:
            part_name = item.text()
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个项目！")
                return
            
            # 获取当前项目数据
            if not hasattr(self, 'get_current_item_data'):
                QMessageBox.warning(self, "警告", "系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                QMessageBox.warning(self, "警告", "无法获取当前项目数据！")
                return
            
            # 确认删除
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除零部件 '{part_name}' 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 从数据中删除
                parts = current_data["parts"]
                for i, part in enumerate(parts):
                    if part.get("name") == part_name:
                        del parts[i]
                        break
                
                # 保存数据
                self.save_data()
                
                # 重新加载零部件列表
                self.load_parts_list(current_data)
                
                # 清空详情
                self.clear_part_details()
                
                QMessageBox.information(self, "成功", f"零部件 '{part_name}' 已删除！")
                
        except Exception as e:
            print(f"删除零部件失败: {e}")
            QMessageBox.critical(self, "错误", f"删除零部件失败: {e}")
    
    def rename_part_from_context(self, item):
        """从右键菜单重命名零部件"""
        try:
            old_name = item.text()
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个项目！")
                return
            
            # 获取当前项目数据
            if not hasattr(self, 'get_current_item_data'):
                QMessageBox.warning(self, "警告", "系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                QMessageBox.warning(self, "警告", "无法获取当前项目数据！")
                return
            
            # 获取新名称
            new_name, ok = QInputDialog.getText(
                self, 
                "重命名零部件", 
                f"请输入新的零部件名称:",
                QLineEdit.Normal, 
                old_name
            )
            
            if ok and new_name.strip():
                new_name = new_name.strip()
                
                # 检查名称是否已存在
                parts = current_data["parts"]
                for part in parts:
                    if part.get("name") == new_name and part.get("name") != old_name:
                        QMessageBox.warning(self, "警告", f"零部件名称 '{new_name}' 已存在！")
                        return
                
                # 更新数据
                for part in parts:
                    if part.get("name") == old_name:
                        part["name"] = new_name
                        break
                
                # 保存数据
                self.save_data()
                
                # 重新加载零部件列表
                self.load_parts_list(current_data)
                
                # 如果当前选中的是这个零部件，更新详情
                if self.part_name_edit.text() == old_name:
                    self.part_name_edit.setText(new_name)
                
                QMessageBox.information(self, "成功", f"零部件已重命名为 '{new_name}'！")
                
        except Exception as e:
            print(f"重命名零部件失败: {e}")
            QMessageBox.critical(self, "错误", f"重命名零部件失败: {e}")
    
    def load_part_details(self, item):
        """加载零部件详情"""
        try:
            part_name = item.text()
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                print("当前项目不存在，无法加载零部件详情")
                return
            
            # 检查方法是否存在
            if not hasattr(self, 'get_current_item_data'):
                print("系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                print("无法获取当前项目数据或parts字段不存在")
                return
            
            # 查找对应的零部件
            for part in current_data["parts"]:
                if part.get("name") == part_name:
                    # 加载零部件信息
                    self.part_name_edit.setText(part.get("name", ""))
                    self.part_description.setPlainText(part.get("description", ""))
                    
                    # 加载原理图片
                    self.load_part_principle_images(part.get("principle_images", []))
                    break
        except Exception as e:
            print(f"加载零部件详情失败: {e}")
    
    def clear_part_details(self):
        """清空零部件详情"""
        self.part_name_edit.clear()
        self.part_description.clear()
        self.clear_part_principle_images()
    
    def load_parts_list(self, data):
        """加载零部件列表"""
        try:
            self.parts_list.clear()
            parts = data.get("parts", [])
            for part in parts:
                self.parts_list.addItem(part.get("name", "未命名"))
        except Exception as e:
            print(f"加载零部件列表失败: {e}")
    
    def load_part_principle_images(self, images):
        """加载零部件原理图片"""
        try:
            # 清空现有图片
            self.clear_part_principle_images()
            
            if not images:
                # 显示提示标签
                no_images_label = QLabel("暂无原理图片")
                no_images_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
                no_images_label.setAlignment(Qt.AlignCenter)
                no_images_label.setMinimumHeight(80)
                
                # 先添加弹性空间，再添加标签，确保标签居中
                self.part_principle_images_layout.addStretch()
                self.part_principle_images_layout.addWidget(no_images_label)
                self.part_principle_images_layout.addStretch()
                
                print("显示原理图片提示标签：暂无原理图片")
                return
            
            print(f"开始載入零部件原理圖片縮略圖，圖片數量: {len(images)}")
            
            for i, image_path in enumerate(images):
                try:
                    # 创建缩略图控件
                    thumbnail = ImageThumbnailWidget(
                        image_path, 
                        images, 
                        i, 
                        self, 
                        self.delete_part_principle_image_callback
                    )
                    self.part_principle_images_layout.addWidget(thumbnail)
                except Exception as e:
                    print(f"加载零部件原理图片缩略图失败 {image_path}: {e}")
            
            # 添加弹性空间
            spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.part_principle_images_layout.addItem(spacer)
            print("已添加原理图片弹性空间")
            
            print("零部件原理圖片縮略圖載入完成")
            
        except Exception as e:
            print(f"加载零部件原理图片失败: {e}")
    
    def clear_part_principle_images(self):
        """清空零部件原理图片"""
        try:
            # 清空布局中的所有控件
            while self.part_principle_images_layout.count():
                child = self.part_principle_images_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        except Exception as e:
            print(f"清空零部件原理图片失败: {e}")
    
    def insert_part_principle_image(self):
        """插入零部件原理图片"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "选择零部件原理图片", 
                "", 
                "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file_path:
                self.save_part_principle_image(file_path)
        except Exception as e:
            print(f"插入零部件原理图片失败: {e}")
            QMessageBox.critical(self, "错误", f"插入零部件原理图片失败: {str(e)}")
    
    def save_part_principle_image(self, source_path=None):
        """保存零部件原理图片"""
        try:
            if not source_path:
                return
            
            # 获取当前选中的零部件
            current_item = self.parts_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个零部件！")
                return
            
            part_name = current_item.text()
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个项目！")
                return
            
            # 检查方法是否存在
            if not hasattr(self, 'get_current_item_data'):
                QMessageBox.warning(self, "警告", "系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                QMessageBox.warning(self, "警告", "无法获取当前项目数据！")
                return
            
            # 查找对应的零部件
            target_part = None
            for part in current_data["parts"]:
                if part.get("name") == part_name:
                    target_part = part
                    break
            
            if not target_part:
                return
            
            # 确保principle_images字段存在
            if "principle_images" not in target_part:
                target_part["principle_images"] = []
            
            # 生成目标文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(source_path)[1]
            target_filename = f"part_principle_{timestamp}{file_extension}"
            target_path = os.path.join(self.images_dir, target_filename)
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            
            # 添加到数据
            target_part["principle_images"].append(target_path)
            
            # 保存数据
            self.save_data()
            
            # 重新加载图片
            self.load_part_principle_images(target_part.get("principle_images", []))
            
            QMessageBox.information(self, "成功", "零部件原理图片保存成功！")
            
        except Exception as e:
            print(f"保存零部件原理图片失败: {e}")
            QMessageBox.critical(self, "错误", f"保存零部件原理图片失败: {str(e)}")
    
    def manage_part_principle_images(self):
        """管理零部件原理图片"""
        try:
            current_item = self.parts_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个零部件！")
                return
            
            part_name = current_item.text()
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                QMessageBox.warning(self, "警告", "请先选择一个项目！")
                return
            
            # 检查方法是否存在
            if not hasattr(self, 'get_current_item_data'):
                QMessageBox.warning(self, "警告", "系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                QMessageBox.warning(self, "警告", "无法获取当前项目数据！")
                return
            
            # 查找对应的零部件
            target_part = None
            for part in current_data["parts"]:
                if part.get("name") == part_name:
                    target_part = part
                    break
            
            if not target_part:
                return
            
            images = target_part.get("principle_images", [])
            if not images:
                QMessageBox.information(self, "提示", "该零部件暂无原理图片！")
                return
            
            # 创建图片管理对话框
            dialog = ImageViewerDialog(images, 0, self)
            
            # 添加批量删除按钮
            batch_delete_btn = QPushButton("批量删除")
            batch_delete_btn.clicked.connect(lambda: self.batch_delete_part_principle_images(images, dialog, target_part))
            dialog.button_layout.addWidget(batch_delete_btn)
            
            # 设置列表为多选模式
            dialog.image_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            
            dialog.exec_()
            
        except Exception as e:
            print(f"管理零部件原理图片失败: {e}")
            QMessageBox.critical(self, "错误", f"管理零部件原理图片失败: {str(e)}")
    
    def delete_selected_part_principle_image(self, list_widget, data, dialog):
        """删除选中的零部件原理图片"""
        try:
            current_row = list_widget.currentRow()
            if current_row >= 0 and current_row < len(data):
                image_path = data[current_row]
                
                # 从数据中移除
                data.pop(current_row)
                
                # 删除文件
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # 保存数据
                self.save_data()
                
                # 刷新对话框
                dialog.load_images(data)
                
                QMessageBox.information(dialog, "成功", "零部件原理图片删除成功！")
            else:
                QMessageBox.warning(dialog, "警告", "请先选择要删除的图片！")
                
        except Exception as e:
            print(f"删除零部件原理图片失败: {e}")
            QMessageBox.critical(dialog, "错误", f"删除零部件原理图片失败: {str(e)}")
    
    def batch_delete_part_principle_images(self, list_widget, data, dialog, target_part):
        """批量删除零部件原理图片"""
        try:
            selected_items = list_widget.selectedItems()
            if not selected_items:
                QMessageBox.warning(dialog, "警告", "请先选择要删除的图片！")
                return
            
            # 确认删除
            reply = QMessageBox.question(
                dialog, 
                "确认删除", 
                f"确定要删除选中的 {len(selected_items)} 张图片吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 获取选中的行索引
                selected_rows = []
                for item in selected_items:
                    row = list_widget.row(item)
                    if row >= 0:
                        selected_rows.append(row)
                
                # 按索引倒序删除，避免索引变化
                selected_rows.sort(reverse=True)
                
                deleted_count = 0
                for row in selected_rows:
                    if row < len(data):
                        image_path = data[row]
                        
                        # 从数据中移除
                        data.pop(row)
                        
                        # 删除文件
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            deleted_count += 1
                
                # 保存数据
                self.save_data()
                
                # 刷新对话框
                dialog.load_images(data)
                
                # 重新加载当前零部件的图片
                self.load_part_principle_images(target_part.get("principle_images", []))
                
                QMessageBox.information(dialog, "成功", f"成功删除 {deleted_count} 张零部件原理图片！")
                
        except Exception as e:
            print(f"批量删除零部件原理图片失败: {e}")
            QMessageBox.critical(dialog, "错误", f"批量删除零部件原理图片失败: {str(e)}")
    
    def delete_part_principle_image_callback(self, image_path, current_index):
        """删除零部件原理图片的回调函数"""
        try:
            current_item = self.parts_list.currentItem()
            if not current_item:
                print("未选择零部件，无法删除图片")
                return
            
            part_name = current_item.text()
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                print("当前项目不存在，无法删除图片")
                return
            
            # 检查方法是否存在
            if not hasattr(self, 'get_current_item_data'):
                print("系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                print("无法获取当前项目数据或parts字段不存在")
                return
            
            # 查找对应的零部件
            target_part = None
            for part in current_data["parts"]:
                if part.get("name") == part_name:
                    target_part = part
                    break
            
            if not target_part:
                return
            
            images = target_part.get("principle_images", [])
            if current_index < len(images) and images[current_index] == image_path:
                # 从数据中移除
                images.pop(current_index)
                
                # 删除文件
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # 保存数据
                self.save_data()
                
                # 重新加载图片
                self.load_part_principle_images(images)
                
                QMessageBox.information(self, "成功", "零部件原理图片删除成功！")
                
        except Exception as e:
            print(f"删除零部件原理图片失败: {e}")
            QMessageBox.critical(self, "错误", f"删除零部件原理图片失败: {str(e)}")
    
    def add_part(self):
        """添加零部件"""
        try:
            name, ok = QInputDialog.getText(self, "添加零部件", "请输入零部件名称:")
            if ok and name:
                # 检查当前项目是否存在
                if not hasattr(self, 'current_item') or not self.current_item:
                    QMessageBox.warning(self, "警告", "请先选择一个设备！")
                    return
                
                # 检查方法是否存在
                if not hasattr(self, 'get_current_item_data'):
                    QMessageBox.warning(self, "警告", "系统错误：无法获取当前项目数据方法！")
                    return
                    
                current_data = self.get_current_item_data()
                if not current_data:
                    QMessageBox.warning(self, "警告", "请先选择一个设备！")
                    return
                
                # 确保parts字段存在
                if "parts" not in current_data:
                    current_data["parts"] = []
                
                # 检查是否已存在同名零部件
                for part in current_data["parts"]:
                    if part.get("name") == name:
                        QMessageBox.warning(self, "警告", "该零部件已存在！")
                        return
                
                # 添加新零部件
                new_part = {
                    "name": name,
                    "description": "",
                    "principle_images": []
                }
                current_data["parts"].append(new_part)
                
                # 保存数据
                self.save_data()
                
                # 重新加载零部件列表
                self.load_parts_list(current_data)
                
                # 选择新添加的零部件
                for i in range(self.parts_list.count()):
                    if self.parts_list.item(i).text() == name:
                        self.parts_list.setCurrentRow(i)
                        self.load_part_details(self.parts_list.item(i))
                        break
                
                QMessageBox.information(self, "成功", "零部件添加成功！")
                
        except Exception as e:
            print(f"添加零部件失败: {e}")
            QMessageBox.critical(self, "错误", f"添加零部件失败: {str(e)}")
    
    def delete_part(self):
        """删除零部件"""
        try:
            current_item = self.parts_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个零部件！")
                return
            
            part_name = current_item.text()
            
            # 确认删除
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除零部件 '{part_name}' 吗？\n这将同时删除相关的原理图片！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 检查当前项目是否存在
                if not hasattr(self, 'current_item') or not self.current_item:
                    QMessageBox.warning(self, "警告", "请先选择一个项目！")
                    return
                
                # 检查方法是否存在
                if not hasattr(self, 'get_current_item_data'):
                    QMessageBox.warning(self, "警告", "系统错误：无法获取当前项目数据方法！")
                    return
                    
                current_data = self.get_current_item_data()
                if not current_data or "parts" not in current_data:
                    QMessageBox.warning(self, "警告", "无法获取当前项目数据！")
                    return
                
                # 查找并删除零部件
                for i, part in enumerate(current_data["parts"]):
                    if part.get("name") == part_name:
                        # 删除相关的原理图片文件
                        for image_path in part.get("principle_images", []):
                            if os.path.exists(image_path):
                                os.remove(image_path)
                        
                        # 从数据中移除
                        current_data["parts"].pop(i)
                        break
                
                # 保存数据
                self.save_data()
                
                # 重新加载零部件列表
                self.load_parts_list(current_data)
                
                # 清空详情
                self.clear_part_details()
                
                QMessageBox.information(self, "成功", "零部件删除成功！")
                
        except Exception as e:
            print(f"删除零部件失败: {e}")
            QMessageBox.critical(self, "错误", f"删除零部件失败: {str(e)}")
    
    def setup_parts_auto_save(self):
        """设置零部件自动保存"""
        # 创建定时器
        self.part_name_timer = QTimer()
        self.part_name_timer.setSingleShot(True)
        self.part_name_timer.timeout.connect(self.auto_save_part_name)
        
        self.part_description_timer = QTimer()
        self.part_description_timer.setSingleShot(True)
        self.part_description_timer.timeout.connect(self.auto_save_part_description)
        
        # 连接信号
        self.part_name_edit.textChanged.connect(self.auto_save_part_name)
        self.part_description.textChanged.connect(self.auto_save_part_description)
    
    def auto_save_part_name(self):
        """自动保存零部件名称"""
        self.part_name_timer.start(1000)  # 1秒后保存
        self.save_part_name()
    
    def auto_save_part_description(self):
        """自动保存零部件描述"""
        self.part_description_timer.start(1000)  # 1秒后保存
        self.save_part_description()
    
    def save_part_name(self):
        """保存零部件名称"""
        try:
            current_item = self.parts_list.currentItem()
            if not current_item:
                return
            
            part_name = current_item.text()
            new_name = self.part_name_edit.text().strip()
            
            if not new_name:
                return
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                print("当前项目不存在，无法保存零部件名称")
                return
            
            # 检查方法是否存在
            if not hasattr(self, 'get_current_item_data'):
                print("系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                print("无法获取当前项目数据或parts字段不存在")
                return
            
            # 查找并更新零部件名称
            for part in current_data["parts"]:
                if part.get("name") == part_name:
                    part["name"] = new_name
                    break
            
            # 保存数据
            self.save_data()
            
            # 重新加载零部件列表
            self.load_parts_list(current_data)
            
            # 选择更新后的零部件
            for i in range(self.parts_list.count()):
                if self.parts_list.item(i).text() == new_name:
                    self.parts_list.setCurrentRow(i)
                    break
                    
        except Exception as e:
            print(f"保存零部件名称失败: {e}")
    
    def save_part_description(self):
        """保存零部件描述"""
        try:
            current_item = self.parts_list.currentItem()
            if not current_item:
                return
            
            part_name = current_item.text()
            new_description = self.part_description.toPlainText()
            
            # 检查当前项目是否存在
            if not hasattr(self, 'current_item') or not self.current_item:
                print("当前项目不存在，无法保存零部件描述")
                return
            
            # 检查方法是否存在
            if not hasattr(self, 'get_current_item_data'):
                print("系统错误：无法获取当前项目数据方法！")
                return
                
            current_data = self.get_current_item_data()
            if not current_data or "parts" not in current_data:
                print("无法获取当前项目数据或parts字段不存在")
                return
            
            # 查找并更新零部件描述
            for part in current_data["parts"]:
                if part.get("name") == part_name:
                    part["description"] = new_description
                    break
            
            # 保存数据
            self.save_data()
                    
        except Exception as e:
            print(f"保存零部件描述失败: {e}")
            
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # 使用 Fusion 風格，確保跨平台兼容性
        
        # 設置應用程序信息
        app.setApplicationName("锅炉知识管理系统")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("鍋爐系統管理")
        
        # 創建主窗口
        window = BoilerKnowledge()
        window.show()
        
        # 運行應用程序
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        input("按任意鍵退出...")