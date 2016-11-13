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

create table bmi(
"SUBJECT_ID" TEXT, 
"BMI" REAL
);

.mode csv
.import bmi_out.csv bmi

select * from bmi limit 10;

create table summary_bmi(
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
"FREQ" INTEGER,
"BMI" REAL
);

insert into summary_bmi
select 
summary.SUBJECT_ID, 
DOB, 
DOD, 
LIFESPAN, 
HADM_ID,
SEQ_NUM, 
ICD9_CODE,
ADMITTIME, 
DISCHTIME,
STAYTIME,
FREQ,
BMI
from summary left join bmi
on summary.SUBJECT_ID = bmi.SUBJECT_ID;

ALTER TABLE summary_bmi ADD COLUMN bmi_bin INTEGER;
UPDATE summary_bmi 
SET bmi_bin = 
case when BMI is null then 0 
when BMI < 25 then 1
when BMI > 30 then 3 
else 2 
end;

ALTER TABLE summary_bmi ADD COLUMN age_bin INTEGER;
UPDATE summary_bmi 
SET age_bin = 
case when lifespan is null then 0 
when lifespan < 65 then 1
when lifespan > 75 then 3 
else 2 
end;

ALTER TABLE summary_bmi ADD COLUMN lifespan_bin INTEGER;
UPDATE summary_bmi 
SET lifespan_bin = 
case when lifespan is null then 0 
when lifespan < 50 then 1
when lifespan >= 50 and lifespan < 55 then 2
when lifespan >= 55 and lifespan < 60 then 3
when lifespan >= 60 and lifespan < 65 then 4
when lifespan >= 65 and lifespan < 70 then 5
when lifespan >= 70 and lifespan < 75 then 6
when lifespan >= 75 and lifespan < 80 then 7
when lifespan >= 80 and lifespan < 85 then 8
when lifespan >= 85 and lifespan < 90 then 9
else 10
end;


-- save bmi to csv file
select 
distinct SUBJECT_ID, 
bmi, 
bmi_bin 
from summary_bmi 
where bmi is not null
limit 10;

.mode csv
.output bmi_bin.csv
select 
distinct SUBJECT_ID, 
bmi, 
bmi_bin,
lifespan,
lifespan_bin 
from summary_bmi 
where bmi is not null;
.output stdout

.mode csv
.output bmi_graph.csv
select 
bmi_bin,
lifespan_bin,
count(distinct SUBJECT_ID)
from summary_bmi 
where bmi is not null
group by bmi_bin, lifespan_bin
order by bmi_bin ASC, lifespan_bin ASC
;
.output stdout
