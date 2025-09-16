import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.patches import Circle, Rectangle
from matplotlib.colors import ListedColormap
import matplotlib.patches as patches
import warnings
warnings.filterwarnings('ignore')


class SurfaceCode:
    def __init__(self, d=5):
        """
        d: 码距 (奇数)
        """
        self.d = d
        self.size = 2 * d - 1
        
        self.qubits = np.zeros((self.size, self.size), dtype=int)
        self.data_positions = []
        self.x_check_positions = []
        self.z_check_positions = []
        
        self._setup_grid()
        
        self.x_errors = np.zeros((self.size, self.size), dtype=int)
        self.z_errors = np.zeros((self.size, self.size), dtype=int)

        self.x_syndromes = {}
        self.z_syndromes = {}
    
    def _setup_grid(self):
        for i in range(self.size):
            for j in range(self.size):
                if (i + j) % 2 == 0:
                    self.qubits[i, j] = 1
                    self.data_positions.append((i, j))
                else:
                    if i % 2 == 0:
                        # X稳定子 (绿)
                        self.qubits[i, j] = 2
                        self.x_check_positions.append((i, j))
                    else:
                        # Z稳定子 (黄色)  
                        self.qubits[i, j] = 3
                        self.z_check_positions.append((i, j))
    
    def add_random_error(self, error_rate=0.1):
        """随机添加错误"""
        errors_added = []
        
        print(f"正在向数据量子比特添加错误 (错误率: {error_rate:.1%})...")
        
        for pos in self.data_positions:
            i, j = pos
            if random.random() < error_rate:
                error_type = random.choice(['X', 'Z', 'Y'])
                
                if error_type == 'X':
                    self.x_errors[i, j] = 1
                    errors_added.append((i, j, 'X'))
                    print(f"  → 在位置 ({i:2d},{j:2d}) 的数据量子比特施加了 X错误")
                elif error_type == 'Z':
                    self.z_errors[i, j] = 1
                    errors_added.append((i, j, 'Z'))
                    print(f"  → 在位置 ({i:2d},{j:2d}) 的数据量子比特施加了 Z错误")
                else:  # Y错误 = X + Z
                    self.x_errors[i, j] = 1
                    self.z_errors[i, j] = 1
                    errors_added.append((i, j, 'Y'))
                    print(f"  → 在位置 ({i:2d},{j:2d}) 的数据量子比特施加了 Y错误 (X+Z)")
        
        print(f"总共添加了 {len(errors_added)} 个错误\n")
        return errors_added
    
    def measure_syndromes(self):
        """测量所有稳定子"""
        self.x_syndromes = {}
        self.z_syndromes = {}
        
        print("正在测量稳定子...")
        
        # 测量X稳定子 (检测Z错误)
        active_x_count = 0
        for pos in self.x_check_positions:
            i, j = pos
            syndrome = 0
            neighbors = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
            for ni, nj in neighbors:
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    if (ni, nj) in self.data_positions:
                        syndrome ^= self.z_errors[ni, nj]
            
            self.x_syndromes[pos] = syndrome
            if syndrome == 1:
                active_x_count += 1
                print(f"  → X稳定子 位置 ({i:2d},{j:2d}): 激活 (检测到Z错误)")
        
        # 测量Z稳定子 (检测X错误)
        active_z_count = 0
        for pos in self.z_check_positions:
            i, j = pos
            syndrome = 0
            neighbors = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
            for ni, nj in neighbors:
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    if (ni, nj) in self.data_positions:
                        syndrome ^= self.x_errors[ni, nj]
            
            self.z_syndromes[pos] = syndrome
            if syndrome == 1:
                active_z_count += 1
                print(f"  → Z稳定子 位置 ({i:2d},{j:2d}): 激活 (检测到X错误)")
        
        print(f"稳定子测量完成: {active_x_count} 个X稳定子激活, {active_z_count} 个Z稳定子激活\n")
    
    def simple_decoder(self):
        """贪心解码器"""
        corrections = []
        
        print("开始执行纠错解码...")
        
        # 纠正X错误
        active_z_checks = [pos for pos, val in self.z_syndromes.items() if val == 1]
        
        if active_z_checks:
            print(f"检测到 {len(active_z_checks)} 个激活的Z稳定子，准备纠正X错误:")
        
        for check_pos in active_z_checks:
            i, j = check_pos
            neighbors = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
            for ni, nj in neighbors:
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    if (ni, nj) in self.data_positions:
                        original_error = self.x_errors[ni, nj]
                        self.x_errors[ni, nj] = 1 - self.x_errors[ni, nj]  # 翻转错误
                        corrections.append((ni, nj, 'X'))
                        
                        if original_error == 1:
                            print(f"  → 在位置 ({ni:2d},{nj:2d}) 纠正了X错误 (移除错误)")
                        else:
                            print(f"  → 在位置 ({ni:2d},{nj:2d}) 应用了X纠正 (可能引入新错误)")
                        break
        
        # 纠正Z错误 
        active_x_checks = [pos for pos, val in self.x_syndromes.items() if val == 1]
        
        if active_x_checks:
            print(f"检测到 {len(active_x_checks)} 个激活的X稳定子，准备纠正Z错误:")
        
        for check_pos in active_x_checks:
            i, j = check_pos
            neighbors = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
            for ni, nj in neighbors:
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    if (ni, nj) in self.data_positions:
                        original_error = self.z_errors[ni, nj]
                        self.z_errors[ni, nj] = 1 - self.z_errors[ni, nj]  # 翻转错误
                        corrections.append((ni, nj, 'Z'))
                        
                        if original_error == 1:
                            print(f"  → 在位置 ({ni:2d},{nj:2d}) 纠正了Z错误 (移除错误)")
                        else:
                            print(f"  → 在位置 ({ni:2d},{nj:2d}) 应用了Z纠正 (可能引入新错误)")
                        break
        
        if not corrections:
            print("  → 无需纠错，所有稳定子都已满足")
        
        print(f"总共执行了 {len(corrections)} 次纠正操作\n")
        return corrections
    
    def visualize(self, title="Surface Code", show_errors=True, show_syndromes=True):
        """可视化表面码状态"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        
        # 绘制网格
        for i in range(self.size):
            for j in range(self.size):
                if self.qubits[i, j] == 1:
                    color = 'lightblue'
                    if show_errors:
                        if self.x_errors[i, j] == 1 and self.z_errors[i, j] == 1:
                            color = 'purple'
                        elif self.x_errors[i, j] == 1:
                            color = 'red'
                        elif self.z_errors[i, j] == 1:
                            color = 'orange'
                    
                    circle = Circle((j, self.size-1-i), 0.4, color=color, alpha=0.7)
                    ax.add_patch(circle)
                    ax.text(j, self.size-1-i, 'D', ha='center', va='center', fontweight='bold')
                
                elif self.qubits[i, j] == 2:  # X稳定子
                    color = 'lightgreen'
                    if show_syndromes and (i, j) in self.x_syndromes:
                        if self.x_syndromes[(i, j)] == 1:
                            color = 'darkgreen'
                    
                    square = Rectangle((j-0.4, self.size-1-i-0.4), 0.8, 0.8, 
                                     color=color, alpha=0.7)
                    ax.add_patch(square)
                    ax.text(j, self.size-1-i, 'X', ha='center', va='center', fontweight='bold')
                
                elif self.qubits[i, j] == 3:  # Z稳定子
                    color = 'lightyellow'
                    if show_syndromes and (i, j) in self.z_syndromes:
                        if self.z_syndromes[(i, j)] == 1:
                            color = 'gold'
                    
                    square = Rectangle((j-0.4, self.size-1-i-0.4), 0.8, 0.8, 
                                     color=color, alpha=0.7)
                    ax.add_patch(square)
                    ax.text(j, self.size-1-i, 'Z', ha='center', va='center', fontweight='bold')
        
        ax.set_xlim(-0.5, self.size-0.5)
        ax.set_ylim(-0.5, self.size-0.5)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                      markersize=10, label='Data Qubit (No Error)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                      markersize=10, label='Data Qubit (X Error)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
                      markersize=10, label='Data Qubit (Z Error)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', 
                      markersize=10, label='Data Qubit (Y Error)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightgreen', 
                      markersize=10, label='X Stabilizer (Inactive)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='darkgreen', 
                      markersize=10, label='X Stabilizer (Active)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightyellow', 
                      markersize=10, label='Z Stabilizer (Inactive)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='gold', 
                      markersize=10, label='Z Stabilizer (Active)')
        ]
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
        
        plt.tight_layout()
        plt.show()

# 演示
def demonstrate_error_correction():
    print("=== 表面码量子纠错演示 ===\n")
    surface_code = SurfaceCode(d=5)
    
    print("1. 初始化表面码 (距离 d=5)")
    print(f"   - 数据量子比特数量: {len(surface_code.data_positions)}")
    print(f"   - X稳定子数量: {len(surface_code.x_check_positions)}")
    print(f"   - Z稳定子数量: {len(surface_code.z_check_positions)}")
    
    surface_code.visualize("Initial State - No Errors", show_errors=False, show_syndromes=False)
    
    print("\n2. 随机引入错误...")
    errors = surface_code.add_random_error(error_rate=0.15)
    
    print(f"   添加的错误:")
    for error in errors:
        i, j, error_type = error
        print(f"   - 位置 ({i},{j}): {error_type} 错误")

    surface_code.visualize("After Adding Errors", show_syndromes=False)
    
    print("\n3. 测量稳定子...")
    surface_code.measure_syndromes()

    active_x = sum(1 for v in surface_code.x_syndromes.values() if v == 1)
    active_z = sum(1 for v in surface_code.z_syndromes.values() if v == 1)
    
    print(f"   - 激活的X稳定子数量: {active_x}")
    print(f"   - 激活的Z稳定子数量: {active_z}")

    surface_code.visualize("Syndrome Measurement Results")
    
    print("\n4. 执行纠错...")
    corrections = surface_code.simple_decoder()
    
    print(f"   应用的纠正:")
    for correction in corrections:
        i, j, correction_type = correction
        print(f"   - 位置 ({i},{j}): {correction_type} 纠正")
    
    print("\n5. 验证纠错结果...")

    surface_code.measure_syndromes()
    
    final_active_x = sum(1 for v in surface_code.x_syndromes.values() if v == 1)
    final_active_z = sum(1 for v in surface_code.z_syndromes.values() if v == 1)
    
    print(f"   - 纠错后激活的X稳定子: {final_active_x}")
    print(f"   - 纠错后激活的Z稳定子: {final_active_z}")
    
    surface_code.visualize("After Error Correction")

    total_x_errors = np.sum(surface_code.x_errors)
    total_z_errors = np.sum(surface_code.z_errors)
    
    print(f"\n6. 纠错结果:")
    print(f"   - 剩余X错误: {total_x_errors}")
    print(f"   - 剩余Z错误: {total_z_errors}")
    
    if final_active_x == 0 and final_active_z == 0:
        print("   ✓ 纠错成功！所有稳定子都已满足")
    else:
        print("   纠错失败")

if __name__ == "__main__":
    # 设置随机种子以获得可重现的结果
    random.seed(42)
    np.random.seed(42)
    
    demonstrate_error_correction()