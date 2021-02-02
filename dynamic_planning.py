from numpy import argwhere, sum, zeros, mean, linspace, array
class DynamicPlan:
    def __init__(self, ls, L, m1, m2, N):
        self.results = []
        self.ls, self.L, self.m1, self.m2, self.N = ls, L, m1, m2, N

    def fit(self):
        self.recursion(self.ls, self.L, self.m1, self.m2, self.N)
        self.number = len(self.results)
        self.radio = []
        for item, total_sum in self.results:
            radio = (total_sum + self.m1 + self.m2 + self.N * (len(item)+1)) / self.L
            self.radio.append(radio)
        self.radio_mean = mean(self.radio)
        radios = ['{:.2f}%'.format(i*100) for i in self.radio]
        print([self.number, radios, '{:.2f}%'.format(self.radio_mean*100)])

    def dynamic_plan(self, V, w):
        n = len(w)
        dp = [[0]*(V+1) for i in range(n+1)]
        for i in range(1, n+1):
            for j in range(1, V+1):
                if j < w[i-1]:
                    dp[i][j] = dp[i-1][j]
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i-1][j-w[i-1]]+w[i-1])
        return dp

    def findselected(self, ls, dp):
        item = zeros(len(ls))
        k = dp[-1][-1]
        size = len(ls)
        for i in range(size, 0, -1):
            if (dp[i][k] > dp[i - 1][k]):
                item[i - 1] = 1
                k -= ls[i - 1]

        index = argwhere(item == 1)
        return list(index.flatten())

    def recursion(self, ls, L, m1, m2, N):
        #print('当前运行到: '+ str(ls))
        if len(ls) == 0:
            return
        else:
            V = L - m1 - m2 - N
            w = [value+N for value in ls]
            dp = self.dynamic_plan(V, w)
            index = self.findselected(w, dp)
            w1 = array(w)
            #print(w1[index]-N)
            self.results.append([w1[index]-N, sum(w1[index]-N)])
            w = [ls[i] for i in range(len(ls)) if i not in index]
            self.recursion(w, L, m1, m2, N)


if __name__ == '__main__':
    ls = list(linspace(100, 3000, 30, dtype=int))
    dp = DynamicPlan(ls, 6000, 50, 100, 2)
    dp.fit()
    from pprint import pprint
    pprint(dp, width=130)



