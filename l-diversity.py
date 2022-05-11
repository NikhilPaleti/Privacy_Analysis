import hits
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

df_main = pd.read_csv("./data/HRDataset_v14.csv")
categorical = set(('Employee_Name','Position', 'State', 'Zip', 'DOB', 'Sex', 'MaritalDesc', 'CitizenDesc', 'HispanicLatino', 'RaceDesc', 'DateofHire', 'DateofTermination','TermReason' ,'EmploymentStatus', 'Department', 'ManagerName', 'RecruitmentSource', 'PerformanceScore', 'LastPerformanceReview_Date' ))

categorical_drop = set(('Employee_Name','Position', 'State', 'Zip', 'Sex', 'MaritalDesc', 'CitizenDesc', 'HispanicLatino', 'RaceDesc','TermReason' ,'EmploymentStatus', 'Department', 'ManagerName', 'RecruitmentSource', 'PerformanceScore' ))

def diversity(df, partition, column):
    return len(df[column][partition].unique())

def is_l_diverse(df, partition, sensitive_column, l=2):
    return diversity(df, partition, sensitive_column) >= l

def split(df, partition, column):
    dfp = df[column][partition]
    if column in categorical:
        values = dfp.unique()
        lv = set(values[:len(values)//2])
        rv = set(values[len(values)//2:])
        return dfp.index[dfp.isin(lv)], dfp.index[dfp.isin(rv)]
    else:        
        median = dfp.median()
        dfl = dfp.index[dfp < median]
        dfr = dfp.index[dfp >= median]
        return (dfl, dfr)

def get_spans(df, partition, scale=None):
    spans = {}
    for column in df.columns:
        if column in categorical:
            span = len(df[column][partition].unique())
        else:
            span = df[column][partition].max()-df[column][partition].min()
        if scale is not None:
            span = span/scale[column]
        spans[column] = span
    return spans

def partition_dataset(df, feature_columns, sensitive_column, scale, is_valid):
    finished_partitions = []
    partitions = [df.index]
    while partitions:
        partition = partitions.pop(0)
        spans = get_spans(df[feature_columns], partition, scale)
        for column, span in sorted(spans.items(), key=lambda x:-x[1]):
            lp, rp = split(df, partition, column)
            if not is_valid(df, lp, sensitive_column) or not is_valid(df, rp, sensitive_column):
                continue
            partitions.extend((lp, rp))
            break
        else:
            finished_partitions.append(partition)
    return finished_partitions

feature_columns = ['EmpID', 'Salary']
sensitive_column = 'Salary'

full_spans = get_spans(df_main, df_main.index)
finished_l_diverse_partitions = partition_dataset(df_main, feature_columns, sensitive_column, full_spans, lambda *args: is_l_diverse(*args))


def build_indexes(df):
    indexes = {}
    for column in categorical:
        values = sorted(df[column].unique())
        indexes[column] = { x : y for x, y in zip(values, range(len(values)))}
    return indexes

def get_coords(df, column, partition, indexes, offset=0.1):
    if column in categorical:
        sv = df[column][partition].sort_values()
        l, r = indexes[column][sv[sv.index[0]]], indexes[column][sv[sv.index[-1]]]+1.0
    else:
        sv = df[column][partition].sort_values()
        next_value = sv[sv.index[-1]]
        larger_values = df[df[column] > next_value][column]
        if len(larger_values) > 0:
            next_value = larger_values.min()
        l = sv[sv.index[0]]
        r = next_value
    # we add some offset to make the partitions more easily visible
    l -= offset
    r += offset
    return l, r

def get_partition_rects(df, partitions, column_x, column_y, indexes, offsets=[0.1, 0.1]):
    rects = []
    for partition in partitions:
        xl, xr = get_coords(df, column_x, partition, indexes, offset=offsets[0])
        yl, yr = get_coords(df, column_y, partition, indexes, offset=offsets[1])
        rects.append(((xl, yl),(xr, yr)))
    return rects

df_main.drop('DOB', axis=1, inplace=True)
df_main.drop('LastPerformanceReview_Date',  axis=1, inplace=True)
df_main.drop('DateofTermination', axis=1, inplace=True)
df_main.drop('DateofHire',  axis=1, inplace=True)

indexes = build_indexes(df_main)
column_x, column_y = feature_columns[:2]
l_diverse_rects = get_partition_rects(df_main, finished_l_diverse_partitions, column_x, column_y, indexes, offsets=[0.0, 0.0])


def get_bounds(df_main, column, indexes, offset=1.0):
    if column in categorical:
        return 0-offset, len(indexes[column])+offset
    return df_main[column].min()-offset, df_main[column].max()+offset

def plot_rects(df_main, ax, rects, column_x, column_y, edgecolor='black', facecolor='none'):
    for (xl, yl),(xr, yr) in rects:
        ax.add_patch(patches.Rectangle((xl,yl),xr-xl,yr-yl,linewidth=1,edgecolor=edgecolor,facecolor=facecolor, alpha=0.5))
    ax.set_xlim(*get_bounds(df_main, column_x, indexes))
    ax.set_ylim(*get_bounds(df_main, column_y, indexes))
    ax.set_xlabel(column_x)
    ax.set_ylabel(column_y)

plt.figure(figsize=(20,20))
ax = plt.subplot(111)
plot_rects(df_main, ax, l_diverse_rects, column_x, column_y, edgecolor='b', facecolor='b')
# plot_rects(df_main, ax, rects, column_x, column_y, facecolor='r')
plt.scatter(df_main[column_x], df_main[column_y])
plt.show()