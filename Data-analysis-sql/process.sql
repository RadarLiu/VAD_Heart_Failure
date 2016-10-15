select cast((julianday(DISCHTIME) - julianday(ADMITTIME)) as int) from admissions;

CREATE TABLE lifespan(
"SUBJECT_ID" TEXT,
"DOB" TEXT,
"DOD" TEXT,
"LIFESPAN" INTEGER);

insert into lifespan 
select 
SUBJECT_ID, 
DOB, 
DOD, 
cast(((julianday(DOD) -julianday(DOB))/365) as int) 
from patients 
where (julianday(DOD) -julianday(DOB))/365 < 100;

CREATE TABLE valid_diagnoses(
"SUBJECT_ID" TEXT,
  "HADM_ID" TEXT,
  "SEQ_NUM" TEXT,
  "ICD9_CODE" TEXT
);

select count (distinct (SUBJECT_ID)) from valid_diagnoses; --5232

CREATE TABLE hp_staytime(
"SUBJECT_ID" TEXT,
"HADM_ID" TEXT,
"ADMITTIME" TEXT,
"DISCHTIME" TEXT,
"STAYTIME" INTEGER);

insert into hp_staytime 
select 
SUBJECT_ID, 
HADM_ID, 
ADMITTIME, 
DISCHTIME, 
cast((julianday(DISCHTIME) - julianday(ADMITTIME)) as int) 
from admissions 
where SUBJECT_ID in (select SUBJECT_ID from lifespan);

select count (distinct (SUBJECT_ID)) from hp_staytime; --5232

CREATE TABLE hp_stay(
"SUBJECT_ID" TEXT,
"HADM_ID" TEXT,
"ADMITTIME" TEXT,
"DISCHTIME" TEXT,
"STAYTIME" INTEGER,
"FREQ" INTEGER);

insert into hp_stay
select a.*, 
(select count(*) from hp_staytime b  
	where a.SUBJECT_ID = b.SUBJECT_ID 
	and a.ADMITTIME >= b.ADMITTIME) as cnt
from hp_staytime a;


create table summary(
"SUBJECT_ID" TEXT,
"DOB" TEXT,
"DOD" TEXT,
"LIFESPAN" INTEGER,
"HADM_ID" TEXT,
"SEQ_NUM" TEXT,
"ICD9_CODE" TEXT,
"ADMITTIME" TEXT,
"DISCHTIME" TEXT,
"STAYTIME" INTEGER,
"FREQ" INTEGER
);

insert into summary
select 
lifespan.SUBJECT_ID, 
lifespan.DOB, 
lifespan.DOD, 
lifespan.LIFESPAN, 
valid_diagnoses.HADM_ID,
valid_diagnoses.SEQ_NUM, 
valid_diagnoses.ICD9_CODE,
hp_stay.ADMITTIME, 
hp_stay.DISCHTIME,
hp_stay.STAYTIME,
hp_stay.FREQ
from lifespan join valid_diagnoses join hp_stay
on lifespan.SUBJECT_ID = valid_diagnoses.SUBJECT_ID
and valid_diagnoses.HADM_ID = hp_stay.HADM_ID;

select count(*) from summary;	--131697
select count(*) from valid_diagnoses;


select count(distinct SUBJECT_ID) from summary where FREQ = 2;	--1939

select count(distinct SUBJECT_ID) from summary 
where FREQ = 2 and ICD9_CODE =  "42731";	--844

select avg(a.afterlife)
from(
	select SUBJECT_ID,  avg(cast((julianday(DOD) - julianday(DISCHTIME)) as int)) as afterlife from summary 
	where FREQ = 1 and SUBJECT_ID in 
	(
		select distinct SUBJECT_ID from summary 
		where FREQ = 2 and ICD9_CODE =  "4019"
	)
) a;  --428


select avg(d.afterlife)
from(
	select SUBJECT_ID,  avg(cast((julianday(DOD) - julianday(DISCHTIME)) as int)) as afterlife from summary 
	where FREQ = 1 and SUBJECT_ID in 
		(select a.SUBJECT_ID
		from 
		(select distinct SUBJECT_ID from summary 
		where FREQ = 2 and ICD9_CODE =  "42731") a 
		left join
		(select distinct SUBJECT_ID from summary 
		where FREQ = 3) b
		on a.SUBJECT_ID = b.SUBJECT_ID
		where b.SUBJECT_ID is null
		)
	group by SUBJECT_ID
	)d;


select count(a.SUBJECT_ID)
from 
(select distinct SUBJECT_ID from summary 
where FREQ = 2 and ICD9_CODE =  "42731") a 
inner join
(select distinct SUBJECT_ID from summary 
where FREQ = 3 and ICD9_CODE = "41401") b
on a.SUBJECT_ID = b.SUBJECT_ID;

select avg(d.afterlife)
from(
	select SUBJECT_ID,  avg(cast((julianday(DOD) - julianday(DISCHTIME)) as int)) as afterlife from summary 
	where FREQ = 1 and SUBJECT_ID in 
		(
			select a.SUBJECT_ID
			from 
			(select distinct SUBJECT_ID from summary 
			where FREQ = 2 and ICD9_CODE =  "42731") a 
			inner join
			(select distinct SUBJECT_ID from summary 
			where FREQ = 3 and ICD9_CODE = "41401") b
			on a.SUBJECT_ID = b.SUBJECT_ID
		)
	group by SUBJECT_ID
	)d;

select count(a.SUBJECT_ID)
from 
		(select distinct SUBJECT_ID from summary 
		where FREQ = 1) a 
		left join
		(select distinct SUBJECT_ID from summary 
		where FREQ = 2) b
		on a.SUBJECT_ID = b.SUBJECT_ID
		where b.SUBJECT_ID is null
		;

