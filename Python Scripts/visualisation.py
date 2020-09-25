import settings as settings
from Data_Scrapper import create_connection
import pandas as pd
import tkinter
import matplotlib
import matplotlib.pyplot as plt
import random
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import seaborn as sns

matplotlib.use("TkAgg")

#Sql Query to get Movie Name, Runtime and Ratings
def get_time_and_ratings(conn):
    sql_statement = "select Movie_Name,Movie_RunTime,Movie_Rating from MOVIE_MASTER"
    df = pd.read_sql_query(sql_statement, conn)
    return df

#Sql query to get votes and Movie rating
def get_votes_and_ratings(conn):
    sql_statement = sql_statement = "select Movie_Name,Movie_Votes_Count,Movie_Rating from MOVIE_MASTER"
    df = pd.read_sql_query(sql_statement, conn)
    return df

#Sql query to get average rating per Genre
def average_per_genre(conn):
    sql_statement = "select round(avg(m.Movie_Rating),2) as Average_Rating,round(avg(m.Movie_Runtime),2) as Average_Runtime,g.Movie_Genre from MOVIE_MASTER as m join MOVIE_GENRE_MAPPER as g on m.Movie_Name = g.Movie_Name group by g.Movie_Genre order by Average_Rating desc,Average_Runtime desc"
    df = pd.read_sql_query(sql_statement, conn)
    return df

#Sql query to get avg runtime and movie genre
def average_per_genre_runtime(conn):
    sql_statement = "select round(avg(m.Movie_Runtime),2) as Average_Runtime,g.Movie_Genre from MOVIE_MASTER as m join MOVIE_GENRE_MAPPER as g on m.Movie_Name = g.Movie_Name group by g.Movie_Genre order by Average_Runtime desc"
    df = pd.read_sql_query(sql_statement, conn)
    return df


def cluster(conn):
    sql_statement = "select m.Movie_Runtime,m.Movie_Rating,m.Movie_Name,g.Movie_Genre from MOVIE_GENRE_MAPPER as g left join MOVIE_MASTER as m on m.Movie_Name = g.Movie_Name"
    df = pd.read_sql_query(sql_statement, conn)
    return df

#Plot scatter plot function
def plot_scatter(df_x,df_y,ptitle,xtitle,ytitle):
    plt.scatter(df_x,df_y)
    plt.title(ptitle)
    plt.xlabel(xtitle)
    plt.ylabel(ytitle)
    plt.grid(True)

#plot graph function
def plot_graph(df_x,df_y,ptitle,xtitle,ytitle):
    plt.plot(df_x,df_y)
    plt.title(ptitle)
    plt.xlabel(xtitle)
    plt.ylabel(ytitle)
    plt.grid(True)

def get_random_color(data,key):
    color_dict = {}
    for idx in data[key].unique():
        color_dict[idx] ="#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
    return color_dict

#K-means clustering function
def k_means_algo(cluster_data,no_of_clusters):
    kmeans = KMeans(n_clusters=no_of_clusters, precompute_distances="auto", n_jobs=-1)
    y = kmeans.fit_predict(cluster_data[['Movie_Rating','Movie_RunTime']])
    cluster_data['Cluster'] = y
    reduced_data = PCA(n_components=2).fit_transform(cluster_data[['Movie_Rating','Movie_RunTime','Cluster']])
    results = pd.DataFrame(reduced_data,columns=['pca1','pca2'])
    return cluster_data,results

if __name__ == '__main__':

    conn = create_connection(settings.DB_PATH)

    plt.figure(8)


#Scatter plot of Ratings and Runtime for a movie
    time_rating_df = get_time_and_ratings(conn)
    figs, axes = plt.subplots(1,2)
    sns.distplot(time_rating_df.Movie_Rating,ax=axes[0]);
    sns.distplot(time_rating_df.Movie_RunTime,ax=axes[1]);
    plt.show()
    plot_scatter(
        time_rating_df.Movie_RunTime,
        time_rating_df.Movie_Rating,
        'Scatter plot Movie Run Time vs Ratings',
        'Runtime',
        'Ratings'
        )
    plt.legend()
    plt.show()
#------------------------------------------------

#Scatter plot of Ratings and Number of Votes for a movie
    votes_rating_df = get_votes_and_ratings(conn)
    plot_scatter(
        votes_rating_df.Movie_Rating,
        votes_rating_df.Movie_Votes_Count,
        'Scatter plot Number of Votes vs Ratings',
        'Ratings',
        'Number of Votes'
        )
    plt.show()



    avg_genre_df = average_per_genre(conn)
#-------------------------------------------------------

#Plot Average Rating and Movie Genre
    plot_graph(avg_genre_df.Movie_Genre,
        avg_genre_df.Average_Rating,
        'Movie Genre vs Average Rating',
        'Movie Genre',
        'Average Rating'
        )
    plt.show()
#-----------------------------------

    avg_genre_runtime = average_per_genre_runtime(conn)

#Plot Average Runtime and Movie Genre
    plot_graph(avg_genre_runtime.Movie_Genre,
        avg_genre_runtime.Average_Runtime,
        'Movie Genre vs Average runtime',
        'Movie Genre',
        'Average Runtime')

    plt.show()
#----------------------------------------

# Scatter plot of Ratings and Runtime for a movie
    fig,axes = plt.subplots(2,1)
    sample = cluster(conn)
    sns.set_style("whitegrid")

    sns.boxplot(x = 'Movie_Genre', y = 'Movie_Rating', data = sample,ax=axes[0])
    sns.boxplot(x = 'Movie_Genre', y = 'Movie_RunTime', data = sample,ax=axes[1])
    fig, ax = plt.subplots()
    color_dict = {}
    color_dict = get_random_color(sample,'Movie_Genre')
    color = color_dict.values()
    grouped = sample.groupby('Movie_Genre')
    for key, group in grouped:
        group.plot(ax=ax, kind='scatter', x='Movie_Rating', y='Movie_RunTime', label=key, color=color_dict[key])


    plt.title("Movie_Rating vs Movie_RunTime")
    plt.xlabel("Movie_Rating")
    plt.ylabel("Movie_RunTime")
    plt.grid(True)
    plt.legend()
    plt.show()

#--------------------------------------------

#Performing K- Means Clustering
    cluster = pd.DataFrame(sample, columns=['Movie_Rating','Movie_RunTime','Movie_Genre'])
    cluster,results = k_means_algo(cluster,3)
    # Principal component Plot
    sns.scatterplot(x="pca1", y="pca2", hue=cluster['Cluster'], data=results)
    plt.title('K-means Clustering with 2 dimensions')
    plt.show()
#--------------------------------------------------------------------------

#Clusters and Genre Plot
    color_dict_genre = get_random_color(cluster,'Movie_Genre')
    color = color_dict_genre.values()
    grouped = cluster.groupby('Cluster')


    for key, group in grouped:
        fig, ax = plt.subplots()
        grouped_genre = group.groupby('Movie_Genre')
        for x,group_genre in grouped_genre:
            group_genre.plot(ax=ax,kind='scatter', x='Movie_Rating', y='Movie_RunTime', label=x, color=color_dict_genre[x])

        plt.title("Movie_Rating vs Movie_RunTime Cluster"+str(key))
    plt.xlabel("Movie_Rating")
    plt.ylabel("Movie_RunTime")
    plt.grid(True)
    plt.legend()
    plt.show()
# -------------------------
