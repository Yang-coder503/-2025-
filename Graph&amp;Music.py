import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import cdist
import heapq
import math
from collections import defaultdict, Counter

#数据读取与预处理
df = pd.read_csv(r"D:\Graph\ClassicHit.csv")
print("数据集前5行：")
print(df.head())
print(f"\n数据集基本信息：{df.shape[0]}首歌，{df.shape[1]}列特征")


feature_cols = [
    'Duration', 'Danceability', 'Energy', 'Key', 'Loudness',
    'Speechiness', 'Acousticness', 'Liveness', 'Tempo',
    'Valence', 'Popularity', 'Instrumentalness'
]
#将读取到的数据进行归一化
#X作为字典保存列名作为键，行名作为值，并取出所有值进行归一化，每一行是一首歌
X = df[feature_cols].values
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
print(f"\n标准化后特征矩阵形状：{X_scaled.shape}")

# 计算任意两个曲目距离矩阵（欧式距离，权重越小越相似）
distance_matrix = cdist(X_scaled, X_scaled, metric='euclidean')
print(f"距离矩阵形状：{distance_matrix.shape}")


#核心类定义
class Graph:
    def __init__(self, directed=False):
        self.adj = {}  # 邻接表：{node: {neighbor: weight}}
        self.directed = directed

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = {}

    def add_edge(self, node1, node2, weight):
        self.add_node(node1)
        self.add_node(node2)
        self.adj[node1][node2] = weight
        if not self.directed:
            self.adj[node2][node1] = weight

    def get_nodes(self):
        return list(self.adj.keys())

#定义并查集，辅助实现kruskal算法
class DSU:
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
#查找操作，根节点的父亲指针指向自己，其它节点的指针指向父亲，递归查找
    def find(self, i):
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])  # 路径压缩
        return self.parent[i]
#合并操作，合并两个不同的几何，先找到各自的根节点，如果不同，则将其中一个的根设置为另一个的根
    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_j] = root_i
            return True
        return False


#数据抽样
total_songs = len(df)
sample_size = 2000
#设置种子使结果可复现
np.random.seed(42)
sample_indices = np.random.choice(total_songs, sample_size, replace=False)
sampled_distance_matrix = distance_matrix[sample_indices, :][:, sample_indices]
sampled_df = df.iloc[sample_indices].reset_index(drop=True)
sampled_song_names = sampled_df["Track"].tolist()

print(f"\n抽样后曲目数量：{len(sampled_song_names)}")
print(f"距离矩阵形状：{sampled_distance_matrix.shape}")


#创建图
# 曲目-曲目 , 曲目-体裁 , 曲目-艺术家 三层网络
base_graph = Graph(directed = False)

#向图中加入带权曲目-曲目边，这个图是完全图，任意两个曲目之间都有边
for i in range(len(sampled_song_names)):
    song_i = sampled_song_names[i]
    base_graph.add_node(song_i)
    for j in range(i + 1, len(sampled_song_names)):
        song_j = sampled_song_names[j]
        weight = sampled_distance_matrix[i, j]
        base_graph.add_edge(song_i, song_j, weight)

#向图中加入曲目-体裁边(权重=1)
#遍历数据集中的每一行，给曲目和体裁之间加上边，但是体裁和体裁之间没有边
for _, row in sampled_df.iterrows():
    track = row["Track"]
    genre = row["Genre"]
    base_graph.add_edge(track, genre, weight=1)

#曲目-音乐家边（权重=1）
for _, row in sampled_df.iterrows():
    track = row["Track"]
#取出艺术家的名字，生成曲目和艺术家之间的边，艺术家和艺术家之间没有直接的边相连
    artists = [a.strip() for a in row["Artist"].split(",") if a.strip()]
    for artist in artists:
        base_graph.add_edge(track, artist, weight=1)


#构建类型—类型网络，生成音乐类型之间的发展关系
#以体裁为键，曲目名称为值，找出某体裁下的所有音乐
genre_graph = Graph(directed = False)
genre_to_tracks = defaultdict(list)

for _, row in sampled_df.iterrows():
    genre = row["Genre"]
    track = row["Track"]
    genre_to_tracks[genre].append(track)
all_genres = list(genre_to_tracks.keys())

#定义辅助计算最小距离函数，先计算A中每个元素到B的最小距离之和再取平均
def calculate_single_dir_weight(tracks_a, tracks_b, graph):
    min_distances_a_to_b = []

    for t1 in tracks_a:
        min_dist_for_t1 = float('inf')
        found_neighbor = False

        for t2 in tracks_b:
            if t2 in graph.adj.get(t1, {}):
                current_distance = graph.adj[t1][t2]
                found_neighbor = True

                if current_distance < min_dist_for_t1:
                    min_dist_for_t1 = current_distance

        if found_neighbor:
            min_distances_a_to_b.append(min_dist_for_t1)

    if min_distances_a_to_b:
        return np.mean(min_distances_a_to_b)
    else:
        return float('inf')

for i in range(len(all_genres)):
    g1 = all_genres[i]
    tracks_g1 = genre_to_tracks[g1]

    for j in range(i + 1, len(all_genres)):
        g2 = all_genres[j]
        tracks_g2 = genre_to_tracks[g2]

        w_g1_to_g2 = calculate_single_dir_weight(tracks_g1, tracks_g2, base_graph)
        w_g2_to_g1 = calculate_single_dir_weight(tracks_g2, tracks_g1, base_graph)

        if w_g1_to_g2 != float('inf') or w_g2_to_g1 != float('inf'):
            valid_weights = [w for w in [w_g1_to_g2, w_g2_to_g1] if w != float('inf')]
            avg_min_weight = np.mean(valid_weights)
            genre_graph.add_edge(g1, g2, avg_min_weight)
#体裁A到体裁B距离依赖该体裁下的乐曲的相似程度
print("\n类型网络已生成")
print(f"类型网络节点数：{len(genre_graph.get_nodes())}")
print(f"类型网络边数：{sum(len(edges) for edges in genre_graph.adj.values()) // 2}")  # 无向图除以2


#构建音乐家—音乐家图，输出最具影响力的前二十位音乐家
#以音乐家为键，获取音乐家所有的曲目
artist_graph = Graph(directed = False)
artist_to_tracks = defaultdict(list)
for _, row in sampled_df.iterrows():
    track = row["Track"]
    artists = [a.strip() for a in row["Artist"].split(",") if a.strip()]
    for artist in artists:
        artist_to_tracks[artist].append(track)
all_artists = list(artist_to_tracks.keys())

#计算两个音乐家之间的平均曲目距离
for i in range(len(all_artists)):
    a1 = all_artists[i]
    tracks_a1 = artist_to_tracks[a1]

    for j in range(i + 1, len(all_artists)):
        a2 = all_artists[j]
        tracks_a2 = artist_to_tracks[a2]

        w_a1_to_a2 = calculate_single_dir_weight(tracks_a1, tracks_a2, base_graph)
        w_a2_to_a1 = calculate_single_dir_weight(tracks_a2, tracks_a1, base_graph)

        if w_a1_to_a2 != float('inf') or w_a2_to_a1 != float('inf'):
            valid_weights = [w for w in [w_a1_to_a2, w_a2_to_a1] if w != float('inf')]
            avg_min_weight = np.mean(valid_weights)
            artist_graph.add_edge(a1, a2, avg_min_weight)
#音乐家之间的相似性同样依赖该音乐家的所有乐曲与另一个音乐家的所有乐曲的平均距离
print("\n音乐家网络已生成")
print(f"音乐家网络节点数：{len(artist_graph.get_nodes())}")
print(f"音乐家网络边数：{sum(len(edges) for edges in artist_graph.adj.values()) // 2}")


def prim_mst(graph, start_node=None):
    if not graph.get_nodes():
        return 0.0, []
    start_node = start_node or graph.get_nodes()[0]
    visited = {start_node}
    min_heap = [(weight, start_node, neighbor) for neighbor, weight in graph.adj[start_node].items()]
    heapq.heapify(min_heap)
    mst_edges = []
    total_weight = 0.0

    while min_heap and len(visited) < len(graph.get_nodes()):
        weight, u, v = heapq.heappop(min_heap)
        if v not in visited:
            visited.add(v)
            total_weight += weight
            mst_edges.append((u, v, weight))
            for neighbor, w in graph.adj[v].items():
                if neighbor not in visited:
                    heapq.heappush(min_heap, (w, v, neighbor))
    return total_weight, mst_edges


def kruskal_mst(graph):
    all_edges = []
    for u in graph.get_nodes():
        for v, weight in graph.adj[u].items():
            if u < v:  # 避免重复边
                all_edges.append((weight, u, v))
    all_edges.sort()  # 按权重升序排序

    dsu = DSU(graph.get_nodes())
    mst_edges = []
    total_weight = 0.0

    for weight, u, v in all_edges:
        if len(mst_edges) == len(graph.get_nodes()) - 1:
            break
        if dsu.union(u, v):
            total_weight += weight
            mst_edges.append((u, v, weight))
    return total_weight, mst_edges


#构建曲目相似网络
print("曲目相似性分析")
track_graph = Graph(directed = False)
#仅保留乐曲——乐曲边
for i in range(len(sampled_song_names)):
    song_i = sampled_song_names[i]
    for j in range(i + 1, len(sampled_song_names)):
        song_j = sampled_song_names[j]
        weight = sampled_distance_matrix[i, j]
        track_graph.add_edge(song_i, song_j, weight)

track_mst_weight, track_mst_edges = kruskal_mst(track_graph)
print(f"总权重{track_mst_weight:.4f}")
print(f"边数{len(track_mst_edges)}")


#曲目聚类
print("曲目聚类分析")
#将边按权重的降序排列
sorted_mst_edges = sorted(track_mst_edges, key=lambda x: x[2], reverse=True)
#删除权重最大的18条边
remaining_edges = sorted_mst_edges[18:] if len(sorted_mst_edges) >= 18 else sorted_mst_edges[-18:]

# 构建剩余边的连通分量
cluster_dsu = DSU(sampled_song_names)
for u, v, _ in remaining_edges:
    cluster_dsu.union(u, v)

# 统计每个连通分量（聚类）的曲目
clusters = defaultdict(list)
for song in sampled_song_names:
    root = cluster_dsu.find(song)
    clusters[root].append(song)

#输出信息
cluster_id = 1
total_error = 0
total_songs_clustered = 0
for cluster_songs in clusters.values():
    # 统计该聚类中真实体裁的分布
    true_genres = [sampled_df[sampled_df["Track"] == song]["Genre"].iloc[0] for song in cluster_songs]
    genre_counter = Counter(true_genres)
    # 预测出现次数最多的体裁，并把这个体裁作为该聚类的体裁
    predicted_genre = genre_counter.most_common(1)[0][0]
    # 错误率计算，错误曲目数除所有曲目数
    correct_count = genre_counter[predicted_genre]
    error_count = len(cluster_songs) - correct_count
    error_rate = error_count / len(cluster_songs) if len(cluster_songs) > 0 else 0.0
    # 累计统计
    total_error += error_count
    total_songs_clustered += len(cluster_songs)
    # 输出
    print(f"聚类{cluster_id}：")
    print(f"曲目数量：{len(cluster_songs)}")
    print(f"预测体裁：{predicted_genre}")
    print(f"真实体裁：{dict(genre_counter)}")
    print(f"错误率{error_rate:.4f}")
    cluster_id += 1


#类型传承关系分析
print("类型传承关系分析")
genre_mst_weight, genre_mst_edges = prim_mst(genre_graph)
print(f"总权重{genre_mst_weight:.4f}")
print(f"边数{len(genre_mst_edges)}")
print("\n类型传承MST边表：")
for u, v, weight in genre_mst_edges:
    print(f"  {u} <-> {v} (权重：{weight:.4f})")


#关键传承链路
def get_mst_longest_path(mst_edges, nodes):
    mst_adj = defaultdict(list)
    for u, v, w in mst_edges:
        mst_adj[u].append((v, w))
        mst_adj[v].append((u, w))
#借助队列实现广度优先搜索解决单源最短路径
    def bfs(start):
        dist = {node: -1 for node in nodes}
        prev = {node: None for node in nodes}
        queue = [start]
        dist[start] = 0
        while queue:
            u = queue.pop(0)
            for u, w in mst_adj[u]:
                if dist[v] == -1 :
                    dist[v] = dist[u] + w
                    prev[v] = u
                    queue.append(v)
        farthest_node = max(dist, key=dist.get)
        return farthest_node, dist[farthest_node], prev

#通过两次bfs找出直径，随便选一个起点找出最远点，再找最远点的最远点
    u, _, _ = bfs(nodes[0])
    v, max_dist, prev = bfs(u)

#根据前驱和后继还原路径
    path = []
    current = v
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    return path, max_dist

genre_nodes = genre_graph.get_nodes()
inheritance_path, path_weight = get_mst_longest_path(genre_mst_edges, genre_nodes)
print(f"\n关键传承链路（总权重：{path_weight:.4f}）：")
print(" -> ".join(inheritance_path))


#音乐家影响力分析
print("音乐家影响力分析")
artist_mst_weight, artist_mst_edges = kruskal_mst(artist_graph)
print(f"总权重{artist_mst_weight:.4f}")
print(f"边数{len(artist_mst_edges)}")

#计算音乐家影响力数值，即该音乐家发出的边的权重大小之和
artist_influence = defaultdict(float)
for u, v, weight in artist_mst_edges:
    artist_influence[u] += weight
    artist_influence[v] += weight

#没有边的音乐家影响力记为0
for artist in all_artists:
    if artist not in artist_influence:
        artist_influence[artist] = 0

#前20个最有影响力的音乐家
top20_artists = sorted(artist_influence.items(), key=lambda x: x[1], reverse=True)[:20]
print("\nTop20最有影响力的音乐家：")
print(f"{'排名':<4}{'音乐家':<20}{'影响力分值':<10}")
for rank, (artist, score) in enumerate(top20_artists, 1):
    print(f"{rank:<4}{artist:<20}{score:.4f}")


#通过dijkstra算法还原出最短路径
def reconstruct_path(predecessors, start_node, end_node):
    path = []
#从最后一个节点开始，依据前驱逐个推出路径
    current = end_node
    while current is not None:
        path.append(current)
        current = predecessors[current]
#通过reverse函数反转路径
    path.reverse()
    if path[0] != start_node:
        return None  # 无路径
    return path

def dijkstra_shortest_path(graph, start_node):
    distances = {node: math.inf for node in graph.get_nodes()}
#predecessors存储计算最短路径时节点的前驱
    predecessors = {node: None for node in graph.get_nodes()}
    distances[start_node] = 0
    min_heap = [(0, start_node)]

    while min_heap:
        current_dist, u = heapq.heappop(min_heap)
        if current_dist > distances[u]:
            continue
        for v, weight in graph.adj.get(u, {}).items():
            new_dist = current_dist + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(min_heap, (new_dist, v))
    return distances, predecessors

#选择目标曲目
print("请输入目标曲目名称")
track_a = input()
if track_a in sampled_song_names:
   track_a = track_a

#track_a = sampled_song_names[0]

print(f"\n目标曲目（Track_A）：{track_a}")

#使用dijkstra算法计算A到所有顶点的最短路径
distances, predecessors = dijkstra_shortest_path(base_graph, track_a)

#找A到指定音乐类型的最短路径
print("请输入目标音乐类型")
target_genre = input()
#在图中找到目标的体裁，根据dijkstra算法得到的音乐到目标体裁的最短距离重构出路径
if target_genre in base_graph.get_nodes():
    genre_distance = distances[target_genre]
    genre_path = reconstruct_path(predecessors, track_a, target_genre)
    if genre_path:
        print(f"\n1. Track_A到类型[{target_genre}]的最短路径：")
        print(f"节点序列：{' -> '.join(genre_path)}")
        print(f"总权重：{genre_distance:.4f}")
        print("边详情：")
        for i in range(len(genre_path) - 1):
            u = genre_path[i]
            v = genre_path[i + 1]
            weight = base_graph.adj[u][v]
            print(f"     {u} -> {v} (权重：{weight:.4f})")
    else:
        print(f"\n1. Track_A到类型[{target_genre}]无有效路径")
else:
    print(f"\n1. 类型[{target_genre}]不在数据集中，选择首个类型：{all_genres[0]}")
    target_genre = all_genres[0]
    genre_distance = distances[target_genre]
    genre_path = reconstruct_path(predecessors, track_a, target_genre)
    if genre_path:
        print(f"节点序列：{' -> '.join(genre_path)}")
        print(f"总权重：{genre_distance:.4f}")

#找Track_A到指定音乐家（如The Beatles）的最短路径
print("请输入目标音乐家")
target_artist = input()
artist_list = [a for a in all_artists if target_artist.lower() in a.lower()]
if artist_list:
    target_artist = artist_list[0]
    artist_distance = distances[target_artist]
    artist_path = reconstruct_path(predecessors, track_a, target_artist)
    if artist_path:
        print(f"\n2. Track_A到音乐家[{target_artist}]的最短路径：")
        print(f"   节点序列：{' -> '.join(artist_path)}")
        print(f"   总权重：{artist_distance:.4f}")
        print("   边详情：")
        for i in range(len(artist_path) - 1):
            u = artist_path[i]
            v = artist_path[i + 1]
            weight = base_graph.adj[u][v]
            print(f"     {u} -> {v} (权重：{weight:.4f})")
    else:
        print(f"\n2. Track_A到音乐家[{target_artist}]无有效路径")
else:
    print(f"\n2. 音乐家[{target_artist}]不在数据集中，选择首个音乐家：{all_artists[0]}")
    target_artist = all_artists[0]
    artist_distance = distances[target_artist]
    artist_path = reconstruct_path(predecessors, track_a, target_artist)
    if artist_path:
        print(f"   节点序列：{' -> '.join(artist_path)}")
        print(f"   总权重：{artist_distance:.4f}")

#与Track_A最相似的20首歌曲
track_distances = [(song, distances[song]) for song in sampled_song_names if song != track_a]
similar_20_songs = sorted(track_distances, key=lambda x: x[1])[:20]
print(f"\n3. 与Track_A最相似的20首歌曲（权重越小越相似）：")
print(f"{'排名':<4}{'曲名':<30}{'距离（相似度）':<10}")
print("-" * 44)
for rank, (song, dist) in enumerate(similar_20_songs, 1):
    print(f"{rank:<4}{song[:28]:<30}{dist:.4f}")