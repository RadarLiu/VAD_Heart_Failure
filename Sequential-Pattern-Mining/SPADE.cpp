#include<stdio.h>
#include<string>
#include<list>
#include<cmath>

#define DATASET "xxx.txt"
//#define ENABLE_IDLIST


FILE *fin, *fout;

using namespace std;

//typedef struct itemset list <int>;

typedef struct
{
	int sid;
	int tid;
} id_struct;

typedef struct 
{
	list <list<int>> itemset;
	list <id_struct> id_list;
} node_h;  //id_list as a node horizontally

int total_trans, minsup;

//assuming that max item id<10000
int bucket [10000];

/*
void delete_id_list(list <id_struct> & id_list)
{
	list <id_struct>::iterator it=id_list.begin();
	
	while (it!=id_list.end())
	{
		//id_struct* i=&it;
//		delete &it;
		it++;
	}
	delete &it;
	id_list.clear();
}
*/

void print_id_list(list <id_struct> l)
{
	list <id_struct>::iterator it=l.begin();
	while (it!=l.end())
	{
		fprintf(fout,"<%d %d>\n",it->sid,it->tid);
		it++;
	}
	fprintf(fout,"\n");
}

void print_frequent_seq(list <node_h> k_list)
{
	list <node_h>::iterator it=k_list.begin();
	while (it!=k_list.end())
	{
		list < list<int>>::iterator itt=it->itemset.begin();
		while (itt!=it->itemset.end())
		{
			list <int>::iterator ittt=itt->begin();
			while (ittt!=itt->end())
			{
				fprintf(fout,"%d ",*ittt);
				ittt++;
			}
			itt++;
			if (itt!=it->itemset.end()) fprintf(fout," , ");
		}
		fprintf(fout,"\n");
#ifdef ENABLE_IDLIST
		print_id_list(it->id_list);
#endif
		it++;
	}
}

int count_total_diff_sid(list <id_struct> id_list)
{
	list <id_struct>::iterator it_id_list= id_list.begin();

	int total_diff_sid=0;
	//Warning!!!!!!!!!!!!!!!!the following assumes that all transactions by one SID is packed together in both dataset and id_lists
	//otherwise, a bucket will be needed for duplicate elimination!
	//However, it is important to keep them ordered for sake of performance, so a preprocessing can be added if needed
	int last=-1;
	while (it_id_list!=id_list.end())
	{
		if (last!=(*it_id_list).sid)
		{
			last=(*it_id_list).sid;
			total_diff_sid++;
		}
		it_id_list++;
	}
	return(total_diff_sid);
}

//pruning id_lists with sup<minsuout of k_list
void prune_k_list(list <node_h> & k_list, int minsup)
{
	list <node_h>::iterator it_k_list=k_list.begin();

	while (it_k_list!=k_list.end())
	{
		if (count_total_diff_sid((*it_k_list).id_list)<minsup)
		{
//			delete_id_list((*it_k_list).id_list);   this should be managed/deleted by stl itself, not newed!
			it_k_list=k_list.erase(it_k_list);  //this erase will automatically forward it_k_list after erasing (by return value)
		}
		else it_k_list++;
	}
}

//join basic elements in k-1 list into k-2 list
void join_for_k_2_list (list <id_struct> s1, list <id_struct> s2, list <node_h> &tar, int type, int item1, int item2)
{
	list <id_struct> tmp_id_list;
	if (type==1 || type==3)
	{
		list <id_struct>::iterator it1=s1.begin();
		while (it1!=s1.end())
		{
			list <id_struct>::iterator it2=s2.begin();
			while (it2!=s2.end())
			{
				if((*it1).sid==(*it2).sid)
				{
					if (((type==1 && (*it1).tid==(*it2).tid)) || (type==3 && (*it1).tid>(*it2).tid))
					{
						id_struct* p=new id_struct;
						p->sid=(*it1).sid;
						p->tid=(*it1).tid;
						tmp_id_list.push_back(*p);
						delete p;
						break;
					}
				}
				it2++;
			}
			it1++;
		}
	}
	else if (type==2)
	{
		list <id_struct>::iterator it2=s2.begin();
		while (it2!=s2.end())
		{
			list <id_struct>::iterator it1=s1.begin();
			while (it1!=s1.end())
			{
				if((*it1).sid==(*it2).sid)
				{
					if ( (*it1).tid<(*it2).tid)  //´óÓÚÕß·ÅÔÚÍâÑ­»·
					{
						id_struct* pp=new id_struct;
						pp->sid=(*it2).sid;
						pp->tid=(*it2).tid;
						tmp_id_list.push_back(*pp);
						delete pp;
						break;
					}
				}
				it1++;
			}
			it2++;
		}
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)  //a successful join that generates sid num in id-list>=minsup
	{
		node_h* p=new node_h;
		list<id_struct>::iterator it=tmp_id_list.begin();
		//copy tmp_id_list to id_list of node_h 
		while (it!=tmp_id_list.end())
		{
			id_struct* q=new id_struct;
			q->sid=it->sid;
			q->tid=it->tid;
			p->id_list.push_back(*q);
			delete q;
			it++;
		}
		//resolve item list of node_h
		if (type==1)
		{
			list<int> tmp;
			tmp.push_back(item1);
			tmp.push_back(item2);
			tmp.sort();
			p->itemset.push_back(tmp);
		}
		else if (type==2)
		{
			list<int> tmp;
			tmp.push_back(item1);
			p->itemset.push_back(tmp);
			list<int> tmp2;
			tmp2.push_back(item2);
			p->itemset.push_back(tmp2);
			int tt=5;
		}
		else if (type==3)
		{
			list<int> tmp;
			tmp.push_back(item2);
			p->itemset.push_back(tmp);
			list<int> tmp2;
			tmp2.push_back(item1);
			p->itemset.push_back(tmp2);
		}
		tar.push_back(*p);
		delete p;
	}
}

bool check_for_self_join(node_h node)
{
	//it is guaranteed that element-length of the chain is larger than or equal to 2
	if (node.itemset.size()>=2 && node.itemset.back().size()==1) return(true);
	else return(false);
}

//this function helps to resolve the joined itemsets for type 2 and 3, which are more tricky than type 1 and 4
//called in function match() only
bool process_tricky_type(list <list <int>> shorter, list <list <int>> longer, list <list <int>> &joined_itemset)
{
	int seq_size=shorter.size();
	int seq_count=1;
	list <list <int>>::iterator it1=shorter.begin();
	list <list <int>>::iterator it2=longer.begin();
	//run through all sub-seqs before the last of shorter itemset 1
	while (seq_count<seq_size) 
	{
		list <int> tmp_sub_seq;
		tmp_sub_seq.clear();
		list <int>::iterator itt1=(*it1).begin();
		list <int>::iterator itt2=(*it2).begin();
		if ((*it1).size()!=(*it2).size()) return false;  //sub-seq size mismatch
		while (itt1!=(*it1).end() && itt2!=(*it2).end())
		{
			if (*itt1!=*itt2) return false;  //element mismatch
			tmp_sub_seq.push_back(*itt1);
			itt1++;
			itt2++;
		}
		joined_itemset.push_back(tmp_sub_seq);  //copying old data only, no sorting problem
		seq_count++;
		it1++;
		it2++;
	}
	list <int>::iterator it_longer=(*it2).begin(); //iterator of the last-but-second set of the longer itemset
	list <int> remove_field;  //just a copy of (*it1) for removal test
	list <int>::iterator it_shorter=(*it1).begin();
	while (it_shorter!=(*it1).end())
	{
		remove_field.push_back(*it_shorter);
		it_shorter++;
	}
	while (it_longer!=(*it2).end())
	{
		list <int>::iterator it_shorter=remove_field.begin();
		bool found=false;
		while (it_shorter!=remove_field.end())
		{
			if (*it_shorter==*it_longer)
			{
				remove_field.erase(it_shorter);
				found=true;
				break;
			}
			else it_shorter++;
		}
		if (!found) return(false); //still, prefix mismatch
		it_longer++;
	}
	//removal check completed, it is a match!
	joined_itemset.push_back(*it1); //pointing to the last sub set of itemset_shorter
	//note that the above subset is already sorted, so no sorting is needed here
	it2++;
	joined_itemset.push_back(*it2); //pointing to the last sub set (a single element) of itemset_longer
	return(true);
}


//returns both join type and the joined itemset (for case 3, only the prefix of itemset)
int match(node_h node1, node_h node2, list <list <int>> &joined_itemset)
{
	int possible_type_2_or_3=0;
	if (node1.itemset.size()!=node2.itemset.size())  //might be type 2 or 3
	{
		if ((node2.itemset.size()-node1.itemset.size())==1)
		{
			possible_type_2_or_3=2;
		}
		else if ((node2.itemset.size()-node1.itemset.size())==-1)
		{
			possible_type_2_or_3=3;
		}
		else return 0;  //cannot match
	}

	if (!possible_type_2_or_3)
	{
		int seq_size=node1.itemset.size();
		int seq_count=1;
		list <list <int>>::iterator it1=node1.itemset.begin();
		list <list <int>>::iterator it2=node2.itemset.begin();
		//run through all sub-seqs before the last
		while (seq_count<seq_size) 
		{
			list <int> tmp_sub_seq;
			tmp_sub_seq.clear();
			list <int>::iterator itt1=(*it1).begin();
			list <int>::iterator itt2=(*it2).begin();
			if ((*it1).size()!=(*it2).size()) return 0;  //sub-seq size mismatch
			while (itt1!=(*it1).end() && itt2!=(*it2).end())
			{
				if (*itt1!=*itt2) return 0;  //element mismatch
				tmp_sub_seq.push_back(*itt1);
				itt1++;
				itt2++;
			}
			joined_itemset.push_back(tmp_sub_seq);  //copying old data only, no sorting problem
			seq_count++;
			it1++;
			it2++;
		}
		//deal with the last sub-seq, now both it1 and it2 should be pointing to their respective tails
	//	bool is_ele_atom_1=((*it1).size()>1? true:false);
	//	bool is_ele_atom_2=((*it2).size()>1? true:false);
		bool both_ele_atom=((*it1).size()>1? true:false);
	
		if (both_ele_atom)  //type=1, still need prefix check
		{	
			list <int>::iterator itt1=(*it1).begin();
			list <int>::iterator itt2=(*it2).begin();
			if ((*it1).size()!=(*it2).size()) printf("Size check Error! Length Assumption Violation!\n");
			int size_cnt=1;
			list <int> tmp_sub_seq;
			tmp_sub_seq.clear();
			while (size_cnt<(*it1).size())
			{
				if (*itt1!=*itt2) return 0;  //element mismatch
				tmp_sub_seq.push_back(*itt1);
				itt1++;
				itt2++;
				size_cnt++;
			}
			if ((*itt1)==(*itt2)) return 0; //identical, but self-join not allowed
			tmp_sub_seq.push_back(*itt1);
			tmp_sub_seq.push_back(*itt2);
			tmp_sub_seq.sort();  //sorting needed here
			joined_itemset.push_back(tmp_sub_seq);
			return 1;
		}
		else //type=4, seq join seq
		{
			return 4; //at this time, joined_itemset is only the prefix, needs to be enumerated outside!
		}
	}
	else //possible type 2 or 3
	{
		if (possible_type_2_or_3==2)  //type 2, PB P,C   itemset 1 is shorter sequencially
		{
			bool is_match=process_tricky_type(node1.itemset,node2.itemset,joined_itemset);
			if (!is_match) return 0;
			else return 2;
		}
		else if(possible_type_2_or_3==3)
		{
			bool is_match=process_tricky_type(node2.itemset,node1.itemset,joined_itemset);
			if (!is_match) return 0;
			else return 3;
		}
		else printf ("Type Error While Determining Type 2 or 3!\n");
	}
}

void self_join(node_h node, list <node_h> &new_list)
{
	id_struct tmp;
	list <id_struct> tmp_id_list;
	tmp_id_list.clear();
	list <id_struct>::iterator it1=node.id_list.begin();
	while (it1!=node.id_list.end())
	{
		list <id_struct>::iterator it2=it1;
		it2++;
		while (it2!=node.id_list.end())
		{
			if (it1->sid==it2->sid && it1->tid<it2->tid)
			{
				tmp.sid=it2->sid;
				tmp.tid=it2->tid;
				tmp_id_list.push_back(tmp);
				break;
			}
			it2++;
		}
		it1++;
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)
	{
		node_h new_node;
		new_node.id_list=tmp_id_list;
		node.itemset.push_back(node.itemset.back());
		new_node.itemset=node.itemset;
		new_list.push_back(new_node);
	}
}

bool join_type_1(node_h node1, node_h node2, list <node_h> &new_list, list <list<int>> joined_itemset)
{
	id_struct tmp;
	list <id_struct> tmp_id_list;
	tmp_id_list.clear();
	list <id_struct>::iterator it1=node1.id_list.begin();
	while (it1!=node1.id_list.end())
	{
		list <id_struct>::iterator it2=node2.id_list.begin();
		while (it2!=node2.id_list.end())
		{
			if (it1->sid==it2->sid && it1->tid==it2->tid)
			{
				tmp.sid=it2->sid;
				tmp.tid=it2->tid;
				tmp_id_list.push_back(tmp);
				break;
			}
			it2++;
		}
		it1++;
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)
	{
		node_h new_node;
		new_node.id_list=tmp_id_list;
		new_node.itemset=joined_itemset;
		new_list.push_back(new_node);
		return true;  //found 
	}
	return false;  //not found
}

bool join_type_2(node_h node1, node_h node2, list <node_h> &new_list, list <list<int>> joined_itemset)
{
	id_struct tmp;
	list <id_struct> tmp_id_list;
	tmp_id_list.clear();
	list <id_struct>::iterator it1=node2.id_list.begin(); //last time stamper is on the outside
	while (it1!=node2.id_list.end())
	{
		list <id_struct>::iterator it2=node1.id_list.begin();
		while (it2!=node1.id_list.end())
		{
			if (it1->sid==it2->sid && it1->tid>it2->tid)
			{
				tmp.sid=it1->sid;
				tmp.tid=it1->tid;
				tmp_id_list.push_back(tmp);
				break;
			}
			it2++;
		}
		it1++;
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)
	{
		node_h new_node;
		new_node.id_list=tmp_id_list;
		new_node.itemset=joined_itemset;
		new_list.push_back(new_node);
		return true; //found
	}
	return false; //not found
}

bool join_type_3(node_h node1, node_h node2, list <node_h> &new_list, list <list<int>> joined_itemset)
{
	id_struct tmp;
	list <id_struct> tmp_id_list;
	tmp_id_list.clear();
	list <id_struct>::iterator it1=node1.id_list.begin(); //last time stamper is on the outside
	while (it1!=node1.id_list.end())
	{
		list <id_struct>::iterator it2=node2.id_list.begin();
		while (it2!=node2.id_list.end())
		{
			if (it1->sid==it2->sid && it1->tid>it2->tid)
			{
				tmp.sid=it1->sid;
				tmp.tid=it1->tid;
				tmp_id_list.push_back(tmp);
				break;
			}
			it2++;
		}
		it1++;
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)
	{
		node_h new_node;
		new_node.id_list=tmp_id_list;
		new_node.itemset=joined_itemset;
		new_list.push_back(new_node);
		return true;  //found
	}
	return false;  //not found
}

//join_type_4_three_cases(*it1,*it2,new_list,joined_itemset);
bool join_type_4_three_cases(node_h node1, node_h node2, list <node_h> &new_list, list <list<int>> joined_itemset_prefix)
{
	id_struct tmp;
	list <id_struct> tmp_id_list;
	bool found=false;
	//case 1
	tmp_id_list.clear();
	list <id_struct>::iterator it1=node1.id_list.begin();//last time stamper is on the outside
	while (it1!=node1.id_list.end())
	{
		list <id_struct>::iterator it2=node2.id_list.begin();
		while (it2!=node2.id_list.end())
		{
			if (it1->sid==it2->sid && it1->tid==it2->tid)
			{
				tmp.sid=it1->sid;
				tmp.tid=it1->tid;
				tmp_id_list.push_back(tmp);
				break;
			}
			it2++;
		}
		it1++;
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)
	{
		node_h new_node;
		new_node.id_list=tmp_id_list;
		list <list <int>> joined_itemset=joined_itemset_prefix;
		list <int> sub_itemset;
		sub_itemset.push_back(node1.itemset.back().back());
		sub_itemset.push_back(node2.itemset.back().back());
		sub_itemset.sort();
		joined_itemset.push_back(sub_itemset);
		new_node.itemset=joined_itemset;
		new_list.push_back(new_node);
		found=true;
	}

	//case 2
	tmp_id_list.clear();
	it1=node1.id_list.begin();//last time stamper is on the outside
	while (it1!=node1.id_list.end())
	{
		list <id_struct>::iterator it2=node2.id_list.begin();
		while (it2!=node2.id_list.end())
		{
			if (it1->sid==it2->sid && it1->tid>it2->tid)
			{
				tmp.sid=it1->sid;
				tmp.tid=it1->tid;
				tmp_id_list.push_back(tmp);
				break;
			}
			it2++;
		}
		it1++;
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)
	{
		node_h new_node;
		new_node.id_list=tmp_id_list;
		list <list <int>> joined_itemset=joined_itemset_prefix;
		list <int> sub_itemset;
		sub_itemset.push_back(node2.itemset.back().back());
		joined_itemset.push_back(sub_itemset);
		sub_itemset.clear();
		sub_itemset.push_back(node1.itemset.back().back());
		joined_itemset.push_back(sub_itemset);
		new_node.itemset=joined_itemset;
		new_list.push_back(new_node);
		found=true;
	}

	//case 3
	tmp_id_list.clear();
	it1=node2.id_list.begin();//last time stamper is on the outside
	while (it1!=node2.id_list.end())
	{
		list <id_struct>::iterator it2=node1.id_list.begin();
		while (it2!=node1.id_list.end())
		{
			if (it1->sid==it2->sid && it1->tid>it2->tid)
			{
				tmp.sid=it1->sid;
				tmp.tid=it1->tid;
				tmp_id_list.push_back(tmp);
				break;
			}
			it2++;
		}
		it1++;
	}
	if (count_total_diff_sid(tmp_id_list)>=minsup)
	{
		node_h new_node;
		new_node.id_list=tmp_id_list;
		list <list <int>> joined_itemset=joined_itemset_prefix;
		list <int> sub_itemset;
		sub_itemset.push_back(node1.itemset.back().back());
		joined_itemset.push_back(sub_itemset);
		sub_itemset.clear();
		sub_itemset.push_back(node2.itemset.back().back());
		joined_itemset.push_back(sub_itemset);
		new_node.itemset=joined_itemset;
		new_list.push_back(new_node);
		found=true;
	}
	return found;
}

//generate_k_plus_1_list(k_list,seq_length,found_new_frequent
list <node_h> generate_k_plus_1_list(list <node_h> prev_list,int seq_length,bool &found_new_frequent)
{
	list <node_h> new_list;
	new_list.clear();
	list <node_h>::iterator it1=prev_list.begin();
	while (it1!=prev_list.end())
	{
		//check for self-join, do it alone because only sequence atom can do this
		//self_join generates its own joined_itemset, which is easy
		if (check_for_self_join(*it1)) self_join(*it1,new_list);
		list <node_h>::iterator it2=it1; it2++;
		while (it2!=prev_list.end())
		{
			list <list<int>> joined_itemset;
			joined_itemset.clear();
			int type=match(*it1,*it2,joined_itemset);
			
			if (type==1) //PB  PC
			{
				found_new_frequent|=join_type_1(*it1,*it2,new_list,joined_itemset);
			}
			else if (type==2) //PB P,C
			{
				found_new_frequent|=join_type_2(*it1,*it2,new_list,joined_itemset);
			}
			else if (type==3) //P,B  PC
			{
				found_new_frequent|=join_type_3(*it1,*it2,new_list,joined_itemset);
			}
			else if (type==4) //P,B  P,C
			{
				//joined_itemset is now only the prefix, needs further elaboration for each of the 3 cases
				found_new_frequent|=join_type_4_three_cases(*it1,*it2,new_list,joined_itemset);
			}
			it2++;
		}
		it1++;
	}
	
	return new_list;
}

bool same_itemset(list <list <int>> set1, list <list <int>> set2)
{
	if (set1.size()!=set2.size()) return false;
	list <list <int>>::iterator it1=set1.begin();
	list <list <int>>::iterator it2=set2.begin();
	while (it1!=set1.end())
	{
		if (it1->size()!=it2->size()) return false;
		list <int>::iterator itt1=it1->begin();
		list <int>::iterator itt2=it2->begin();
		while (itt1!=it1->end())
		{
			if (*itt1!=*itt2) return false;
			itt1++;
			itt2++;
		}
		it1++;
		it2++;
	}
	return true;
}

//eliminate duplicated sequences in k_list
list <node_h> duplicate_elimination_for_k_list (list <node_h> k_list)
{
	list <node_h>::iterator it1=k_list.begin();
	while (it1!=k_list.end())
	{
		list <node_h>::iterator it2=it1;
		it2++;
		while (it2!=k_list.end())
		{
			if (same_itemset(it1->itemset,it2->itemset))
			{
				it2=k_list.erase(it2); //auto forward by 1
			}
			else it2++;
		}
		it1++;
	}
	return k_list;
}

int main()
{
	fin=fopen(DATASET,"r");
	fout=fopen("spade.out","w");
	fscanf(fin,"%d%d",&total_trans,&minsup);

	//creating k_1 list
	list <node_h> k_1_list;
	memset(bucket,0,sizeof(bucket));
	for (int i=0;i<total_trans;i++)
	{
		int sid, tid, num,item;
		fscanf(fin,"%d%d%d",&sid, &tid, &num);
		for (int j=0;j<num;j++)
		{
			fscanf(fin,"%d",&item);
			if (!bucket[item])
			{
				bucket[item]=1;
				node_h* p_node_h= new node_h;
				list <int> tmp;
				tmp.push_back(item);
				p_node_h->itemset.push_back(tmp);
				k_1_list.push_back(*p_node_h);
				delete p_node_h;
			}
			list <node_h>::iterator it;
			it=k_1_list.begin();
			while (it!=k_1_list.end())
			{
				if (*((*((*it).itemset.begin())).begin())==item) break;
				it++;
			}
			if (it==k_1_list.end()) printf("Error: existing item in k_1_list lost!\n");
			//insert an id_list record
			id_struct* p_id_struct= new id_struct;
			p_id_struct->sid=sid;
			p_id_struct->tid=tid;
			it->id_list.push_back(*p_id_struct);  //another section of memory?
			delete p_id_struct;
		}
	}

	//pruning k-1 list
	prune_k_list(k_1_list,minsup);

	//generate k-2 list, iteration starts from k-3 generation since an empty prefix can be considered as both ()A and (),A
	list <node_h> k_list;
	list <node_h>:: iterator it1=k_1_list.begin();
	while (it1!=k_1_list.end())
	{
		list <node_h>:: iterator it2=it1;
	//	it2++; allow self-join
		int item1,item2;
		while (it2!=k_1_list.end())
		{
			/*list<list<int>> t1= (*it1).itemset ; // item2= (*it2).itemset.begin().begin()  ;
			list<list<int>>::iterator tt1=t1.begin();
			list<int> t2=(*tt1);
			list <int>::iterator tt2=t2.begin();
			item1=(*tt2);
			*/
			//(((*it1).itemset).begin())
			item1=(*((*(((*it1).itemset).begin())).begin()));
			item2=(*((*(((*it2).itemset).begin())).begin()));
			if (it2!=it1) join_for_k_2_list((*it1).id_list,(*it2).id_list,k_list,1,item1,item2); //join into set, no self-join
			join_for_k_2_list((*it1).id_list,(*it2).id_list,k_list,2,item1,item2); //join sequence left first
			if (it2!=it1) join_for_k_2_list((*it1).id_list,(*it2).id_list,k_list,3,item1,item2); //join sequence right first, avoid 2nd self-join
			it2++;
		}
		it1++;
	}

	print_frequent_seq(k_list);
	//main iteration
	bool found_new_frequent=1;
	int seq_length=2;  
	int tms=0;
	while (1)  //iteration stops when no more new frequent sequence is found
	{
		tms++; printf("%d\n",tms);
		found_new_frequent=false;
		k_list=generate_k_plus_1_list(k_list,seq_length,found_new_frequent);
		if (!found_new_frequent) break;
		k_list=duplicate_elimination_for_k_list(k_list);
		seq_length++;
		print_frequent_seq(k_list);
	}

	fclose(fin);
	fclose(fout);
}
