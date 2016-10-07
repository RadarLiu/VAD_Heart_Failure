#include<stdio.h>
#include<stdlib.h>
#include<string>
#include<set>
#include<vector>
#include<cstring>
#include<sys/time.h>

//#define minsup 2000
//#define minsup 2000
//#define minsup 1
//#define dataset "xxx.txt"
#define max_item 100000

using namespace std;

/*
template <typename T>

void deallocate_container(T& c)

{
  
for (typename T::iterator i = c.begin(); i != c.end(); ++i)

    delete *i;

}
*/


typedef struct node2 pointer_to_fp,*ppointer_to_fp; // pre-declearation
typedef struct node1 //fp-tree node
{  
    int item;
	int sup;
    struct node1* father;
	ppointer_to_fp sons;
}fp,*pfp;

typedef struct node2 //unit of a list pointing to several fp-reee nodes
{  
    pfp point_to;
    struct node2* next;  
}pointer_to_fp,*ppointer_to_fp;

typedef struct node3 //the header table
{  
    int item;
	int sup;
	ppointer_to_fp list;
    struct node3* next;
	struct node3* previous;
}header_table,*pheader_table;  
//header_table == struct node    
//pheader_table == struct node*  

typedef struct node4
{
	set<int> itemset;
	int count_of_this_itemset;
	struct node4* next;
}proj_DB,*pproj_DB;

FILE *fin,*fout;
int in_bucket[max_item];
int level_count[1000];
int total_trans,tid,t_len,iid;
int max_iid;
int minsup;
int max_temp_fp_nodes=0;

pheader_table Main_header_table;
pheader_table last_of_Main_header_table;
vector<int> global_frequent_item_chain;

int alloc_proj_DB=0,alloc_fp=0,alloc_list=0,alloc_table=0;
int deloc_proj_DB=0,deloc_fp=0,deloc_list=0,deloc_table=0;

void insert_with_sort(int item, int support, pheader_table &Head, pheader_table &last_of_header_table)
{
	pheader_table p=Head;
	pheader_table q=Head->next;
	while (q && q->sup>support)	//shortcut safe
	{
		p=q; q=q->next;
	}
	pheader_table t=new header_table; alloc_table++;
	if (!q) last_of_header_table=t;
	t->item=item;
	t->list=new pointer_to_fp; alloc_list++;
		t->list->next=NULL;
		t->list->point_to=NULL;
	t->next=q;
	if (q) q->previous=t;
	t->previous=p;
	p->next=t;
	t->sup=support;
}

void insert_into_fp_tree(int item, pfp &fp_now, pheader_table &H, int count)
//if item  exists as a son, then
	//add the son's sup only;
//else 
	//add p->item as a son of fp_now;
	//link the son's father to fp_now;
//fp_now moves to this son;
{
	ppointer_to_fp finder=fp_now->sons->next;
	ppointer_to_fp pre=fp_now->sons;	//the one before finder on the list, for creating new son
	while (finder)
	{
		if (finder->point_to->item==item) break;
		pre=finder;
		finder=finder->next;
	}
	if (finder)
	{
		finder->point_to->sup+=count;
		fp_now=finder->point_to;
		return;
	}
	// create a new son, linking back to father and header table
	finder=new pointer_to_fp; alloc_list++;
	finder->next=NULL;
	finder->point_to=new fp; alloc_fp++;
		finder->point_to->father=fp_now;
		finder->point_to->item=item;
		finder->point_to->sons=new pointer_to_fp; alloc_list++;
			finder->point_to->sons->next=NULL;
			finder->point_to->sons->point_to=NULL;
		finder->point_to->sup=count;
	//²åÈëheader_tableµÄlistÊ±£¬ÓÃµõÍ°Ç°²å·¨±ÜÃâÎ²²å·¨µÄÏßÐÔ²éÕÒÎ²²¿»òÕß¼ÇÂ¼Î²²¿
	ppointer_to_fp ptr1=H->list->next;
	ppointer_to_fp ptr2=new pointer_to_fp; alloc_list++;
	ptr2->point_to=finder->point_to;
	H->list->next=ptr2;
	ptr2->next=ptr1;

	pre->next=finder;
	fp_now=finder->point_to;

	int ttt=alloc_fp-deloc_fp;
	if (max_temp_fp_nodes<ttt) max_temp_fp_nodes=ttt;
}

void write_global_frequent_item_chain(void)
{
//	fprintf(fout,"%d ",global_frequent_item_chain.size());
	level_count[global_frequent_item_chain.size()]++;

	/*
	for (int i=0;i<global_frequent_item_chain.size();i++)
	{
		fprintf(fout,"%d ",global_frequent_item_chain[i]);
	}
	fprintf(fout,"\n");
	*/
}

void construct_proj_DB(pfp &fp_tree, pheader_table &cond_item, pproj_DB &DB0)
{
	DB0=new proj_DB; alloc_proj_DB++;
	DB0->itemset.clear();
	DB0->count_of_this_itemset=-10000;
	DB0->next=NULL;
	pproj_DB dp1=DB0;
	pproj_DB dp2;

	ppointer_to_fp p=cond_item->list->next;
	while (p)
	{
		pfp fp_node=p->point_to;
		set<int> cond_itemset;
		cond_itemset.clear();
		pfp fp_node2=fp_node->father;
		while (fp_node2!=fp_tree)	//it is assumed (guaranteed) that fp_tree here has at least 2 nodes
		{
			cond_itemset.insert(fp_node2->item);
			fp_node2=fp_node2->father;
		}
		dp2=new proj_DB; alloc_proj_DB++;
		dp2->itemset=cond_itemset;
		dp2->count_of_this_itemset=fp_node->sup;
		dp2->next=NULL;
		dp1->next=dp2;
		dp1=dp2;
		p=p->next;
	}
}

void delete_proj_DB(pproj_DB &DB)
{
	if (!DB) return;
	pproj_DB p=DB;
	pproj_DB q=p->next;

//	deallocate_container(p->itemset);

//	p->itemset.clear();

	while (q)
	{
		delete(p); deloc_proj_DB++;
		p=q; q=q->next;
	}
//	p->itemset.clear();
	delete(p); deloc_proj_DB++;
}

void delete_header_table(pheader_table &table)
{
	if (table==NULL) return;
	pheader_table p=table;
	pheader_table q=p->next;
	while (q)
	{
		ppointer_to_fp pp=p->list;
		ppointer_to_fp qq=pp->next;
		while (qq)
		{
			delete(pp); deloc_list++;
			pp=qq; qq=qq->next;
		}
		delete(pp); deloc_list++;
		delete(p); deloc_table++;
		p=q; q=q->next;
	}
	ppointer_to_fp pp=p->list;
	ppointer_to_fp qq=pp->next;
	while (qq)
	{
		delete(pp); deloc_list++;
		pp=qq; qq=qq->next;
	}
	delete(pp); deloc_list++;
	delete(p); deloc_table++;
}

void delete_fp_tree(pfp &fptree)
{
	if (!fptree) return;
	ppointer_to_fp p=fptree->sons;
	ppointer_to_fp q=p->next;
	while (q)
	{
		if ((p->point_to)) delete_fp_tree(p->point_to);
		delete(p); deloc_list++;
		p=q; q=q->next;
	}
	if ((p->point_to)) delete_fp_tree(p->point_to);
	delete(p); deloc_list++;
	delete(fptree); deloc_fp++;
}

void Mine(pproj_DB &DB)
{
	//1st proj_DB scan
	memset(in_bucket,0,sizeof(int)*(max_iid+2));	//could do not initialize all, but for simplicity..
	pproj_DB cursor=DB->next;
	while (cursor)
	{
		std::set<int>::iterator it=cursor->itemset.begin();
		while(it!=cursor->itemset.end())
		{
			in_bucket[*it]+=cursor->count_of_this_itemset;
			it++;
		}
		cursor=cursor->next;
	}
	//construct header table
	pheader_table table=new header_table; alloc_table++;
	table->item=-10000;	//special value for the root/empty header
	table->sup=-10000;
	table->list=new pointer_to_fp; alloc_list++;
		table->list->point_to=NULL;
		table->list->next=NULL;
	table->next=NULL;
	table->previous=NULL;
	pheader_table last_of_header_table=table;
	for (int i=1;i<=max_iid;i++)	//for each item appears in the bucket
	{
		if (in_bucket[i]>=minsup)
		{
			insert_with_sort(i,in_bucket[i],table,last_of_header_table);
		}
	}

	//2nd Proj_DB scan, construct fp-tree
	pfp fp_tree=new fp; alloc_fp++;
	fp_tree->item=-10000;
	fp_tree->sup=-10000;
	fp_tree->father=NULL;
	fp_tree->sons=new pointer_to_fp; alloc_list++;
		fp_tree->sons->point_to=NULL;
		fp_tree->sons->next=NULL;
		


	int ttt=alloc_fp-deloc_fp;
	if (max_temp_fp_nodes<ttt) max_temp_fp_nodes=ttt;

	cursor=DB->next;
	while(cursor)
	{
		pheader_table p=table->next;
		pfp fp_now=fp_tree;
		//fp_now is the present (position) pointer on the fp-tree
		while (p)
		{
			if (cursor->itemset.find(p->item)!=cursor->itemset.end())	//item found in transaction
			{
				insert_into_fp_tree(p->item,fp_now,p,cursor->count_of_this_itemset);	//add p->item as a son of fp_now; fp_now moves to this son;
			}
			p=p->next;
		}
		cursor=cursor->next;
	}

	pheader_table t1=last_of_header_table;
	while (t1!=table)
	{
		pproj_DB DB0;
		global_frequent_item_chain.push_back(t1->item);
		write_global_frequent_item_chain();
		construct_proj_DB(fp_tree,t1,DB0);
		Mine(DB0);
		global_frequent_item_chain.pop_back();
		delete_proj_DB(DB0);
		t1=t1->previous;
	}
	delete_header_table(table);
	delete_fp_tree(fp_tree);
}


int main(int argc, char** argv)
{
	char* dataset=argv[1];
	minsup=atoi(argv[2]);
	printf("Dataset:%s\n",dataset);
	printf("Minsup:%d\n",minsup);

	fin=fopen(dataset,"r");
	fout=fopen("frequent_itemsets.out","w");
	memset(in_bucket,0,sizeof(in_bucket));
	memset(level_count,0,sizeof(level_count));
	fscanf(fin,"%d",&total_trans);
	max_iid=0;
	printf("1st Main DB Scan\n");	//initialize header table
	for (int i=1;i<=total_trans;i++)
	{
		fscanf(fin,"%d%d",&tid,&t_len);
		for (int j=1;j<=t_len;j++)
		{
			fscanf(fin,"%d",&iid);
			in_bucket[iid]++;
			if (max_iid<iid) max_iid=iid;
		}
	}
	fclose(fin);
	printf("1st DB Scan Completed\n");

	Main_header_table=new header_table; alloc_table++;
	Main_header_table->item=-10000;	//special value for the root/empty header
	Main_header_table->sup=-10000;
	Main_header_table->list=new pointer_to_fp; alloc_list++;
		Main_header_table->list->point_to=NULL;
		Main_header_table->list->next=NULL;
	Main_header_table->next=NULL;
	Main_header_table->previous=NULL;
	last_of_Main_header_table=Main_header_table;
	for (int i=1;i<=max_iid;i++)	//for each item appears in the bucket
	{
		if (in_bucket[i]>=minsup)
		{
			insert_with_sort(i,in_bucket[i],Main_header_table,last_of_Main_header_table);
		}
	}

	//construct main fp-tree
	pfp Main_fp_tree=new fp; alloc_fp++;
	Main_fp_tree->item=-10000;
	Main_fp_tree->sup=-10000;
	Main_fp_tree->father=NULL;
	Main_fp_tree->sons=new pointer_to_fp; alloc_list++;
		Main_fp_tree->sons->point_to=NULL;
		Main_fp_tree->sons->next=NULL;
	printf("2nd Main DB Scan and primary fp-tree construction\n");
	fin=fopen(dataset,"r");
	fscanf(fin,"%d",&total_trans);
	for (int i=1;i<=total_trans;i++)
	{
	//	if (!(i%1000)) printf("Scanning transaction #%d\n",i);
		fscanf(fin,"%d%d",&tid,&t_len);
		set<int> itemset;
		itemset.clear();
		for (int j=1;j<=t_len;j++)
		{
			fscanf(fin,"%d",&iid);
			itemset.insert(iid);
		}
		pheader_table p=Main_header_table->next;
		pfp fp_now=Main_fp_tree;
		//fp_now is the present (position) pointer on the fp-tree
		while (p)
		{
			if (itemset.find(p->item)!=itemset.end())	//item found in transaction
			{
				insert_into_fp_tree(p->item,fp_now,p,1);	//add p->item as a son of fp_now; fp_now moves to this son;
			}
			p=p->next;
		}
	}
	printf("2nd DB Scan Completed\n");
	//main fp-tree construction completed
	pheader_table t1=last_of_Main_header_table;
	int tms=0;
	while (t1!=Main_header_table)
	{
		tms++;
	//	if (!(tms%5)) printf("Mining on %d th frequent item on the primary level...\n",tms);
		pproj_DB DB0;
		global_frequent_item_chain.push_back(t1->item);
		write_global_frequent_item_chain();
		construct_proj_DB(Main_fp_tree,t1,DB0);
		Mine(DB0);
		global_frequent_item_chain.pop_back();
		delete_proj_DB(DB0);
		t1=t1->previous;
	}
	for (int i=1;i<=20;i++)
	{
		printf("Level %d: %d\n",i,level_count[i]);
	}

//	printf("alloc_table:%d\n",alloc_table);
//	printf("deloc_table:%d\n",deloc_table);
//	printf("alloc_proj_DB:%d\n",alloc_proj_DB);
//	printf("deloc_proj_DB:%d\n",deloc_proj_DB);
	printf("alloc_fp_node:%d\n",alloc_fp);
	printf("Max_temp_fp_nodes: %d\n",max_temp_fp_nodes);
//	printf("deloc_fp:%d\n",deloc_fp);
//	printf("alloc_list:%d\n",alloc_list);
//	printf("deloc_list:%d\n",deloc_list);


	fclose(fin);
	fclose(fout);
}
