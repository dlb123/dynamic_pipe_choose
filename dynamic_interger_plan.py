import numpy as np
from copy import deepcopy
import pulp as lp


class DynamicIntergerPlan:
    def __init__(self, weights, nums, L, m1, m2, N):
        self.weights = np.array(weights) + N
        self.nums = nums
        self.max_weight = L - m1 - m2 - N

    def fit(self):
        print('开始运算')
        print('开始动态规划, 计算所有下料分布可能...')
        weight_num_arrays = self.bag_program(self.weights, self.nums, self.max_weight)
        print('动态规划结束,开始线性规划选择最优分布...')
        result = self.integer_program(weight_num_arrays, self.nums)
        print('线性规划完成, 等待输出结果...')
        init = np.array([r[0] for r in result])
        sum1 = np.sum(init, axis=0, dtype=int)
        residual = sum1 - self.nums
        ls = self.one_hot(residual)
        if not ls:
            return init
        for ele in ls:
            x = np.argmax(ele)
            for i, res in enumerate(init):
                if res[x] > 0:
                    init[i] -= ele
                    break
        return init

    def bag_program(self, weights, nums, max_weight):
        """
        动态规划，获取所有可能的背包装满方案
        input:
            weights: lengths array
            nums: numbers array
            max_weight: pipe length
        output:
            program
        """
        weight_num = [[]] * max_weight
        for il, l in enumerate(weights):
            val = np.zeros(len(weights))
            for i in range(l, max_weight + 1, l):
                val[il] += 1
                if val[il] > nums[il]:
                    break
                tmp = deepcopy(weight_num[i - 1])
                tmp.append(deepcopy(val))
                weight_num[i - 1] = tmp
            for i in range(max_weight):
                if weight_num[i]:
                    if i + l < max_weight:
                        vals = deepcopy(weight_num[i])
                        vals_ = []
                        for val in vals:
                            val[il] += 1
                            if val[il] <= nums[il]:
                                vals_.append(val)
                        tmp = deepcopy(weight_num[i + l])
                        tmp.extend(vals_)
                        weight_num[i + l] = tmp
        #return weight_num[-weights[0]:]
        return weight_num

    def integer_program(self, num_arrs, nums):
        """
        input:
            num_arrs: num set
            nums: minimize num
        output:
            result
        """
        num_arrays_list = []
        for vals in num_arrs:
            num_arrays_list.extend(vals)

        nums_mat = np.array(num_arrays_list)
        A = nums_mat.T
        b = nums
        prob = lp.LpProblem("The_GY_Problem", lp.LpMinimize)
        x = [lp.LpVariable("x_%06d" % i, lowBound=0, cat="Integer")
             for i in range(A.shape[1])]

        prob += lp.lpSum(x), "Total_Number"
        try:
            for i in range(len(b)):
                prob += lp.lpSum([A[i][j] * x[j] for j in range(A.shape[1])]) == b[i]#, "lb%04d" % weights[i]

            prob.solve()
        except Exception as e:
            print(str(e))
        #print("\tStatus:", lp.LpStatus[prob.status])
        res = []
        for v in prob.variables():
            if v.varValue:
                res.append((A[:, int(v.name[2:])], v.varValue))
        return res

    def my_append(self, a, b, c):
        for i in range(c):
            a.append(b)
        return a

    def one_hot(self, residual):
        if np.sum(residual) == 0:
            return
        ls = []
        b = np.zeros_like(residual, dtype = int)
        for i, j in enumerate(residual):
            if j:
                b[i] = 1
                b = np.array(b, dtype=int)
                ls = self.my_append(ls, b, int(j))
                b = np.zeros_like(residual, dtype=int)
        return ls


if __name__ == '__main__':
    weights = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1500, 1900, 3000, 5000]
    num = [1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 4, 2, 2]
    max_weight = 6000 - 50 - 100 -2
    m1 =100
    m2=50
    N=2
    L = 6000
    inter = DynamicIntergerPlan(weights, L=6000, nums=num, m1=m1, m2=m2, N=N)
    a = inter.fit()
    a = sorted(a, key= lambda x: np.sum(np.array(x)*weights), reverse=True)

    max1 = np.max(np.sum(np.array(a)*weights, axis=1))
    print(max1)
    for i, num in enumerate(y * weights):
        if np.sum(x*weights) + num <= max1:
            x[i] += y[i]
            y[i] -= y[i]
    a[-2:] = x, y
    print(str(a))
    print(np.sum(np.array(a)*weights, axis=1))

