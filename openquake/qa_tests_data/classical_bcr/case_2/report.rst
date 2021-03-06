Classical BCR test
==================

============== ===================
checksum32     1,808,877,325      
date           2018-10-05T03:04:27
engine_version 3.3.0-git48e9a474fd
============== ===================

num_sites = 11, num_levels = 8

Parameters
----------
=============================== ==================
calculation_mode                'classical_bcr'   
number_of_logic_tree_samples    0                 
maximum_distance                {'default': 200.0}
investigation_time              50.0              
ses_per_logic_tree_path         1                 
truncation_level                3.0               
rupture_mesh_spacing            20.0              
complex_fault_mesh_spacing      20.0              
width_of_mfd_bin                0.5               
area_source_discretization      20.0              
ground_motion_correlation_model None              
minimum_intensity               {}                
random_seed                     42                
master_seed                     0                 
ses_seed                        42                
=============================== ==================

Input files
-----------
==================================== ============================================================================
Name                                 File                                                                        
==================================== ============================================================================
exposure                             `exposure_model.xml <exposure_model.xml>`_                                  
gsim_logic_tree                      `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                                
job_ini                              `job.ini <job.ini>`_                                                        
source                               `source_model.xml <source_model.xml>`_                                      
source_model_logic_tree              `source_model_logic_tree.xml <source_model_logic_tree.xml>`_                
structural_vulnerability             `structural_vulnerability_model.xml <structural_vulnerability_model.xml>`_  
structural_vulnerability_retrofitted `vulnerability_model_retrofitted.xml <vulnerability_model_retrofitted.xml>`_
==================================== ============================================================================

Composite source model
----------------------
========= ======= =============== ================
smlt_path weight  gsim_logic_tree num_realizations
========= ======= =============== ================
b1        1.00000 simple(3)       3/3             
========= ======= =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ======================================================= =========== ======================= =================
grp_id gsims                                                   distances   siteparams              ruptparams       
====== ======================================================= =========== ======================= =================
0      AkkarBommer2010() BooreAtkinson2008() ChiouYoungs2008() rjb rrup rx vs30 vs30measured z1pt0 dip mag rake ztor
====== ======================================================= =========== ======================= =================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=3, rlzs=3)
  0,AkkarBommer2010(): [2]
  0,BooreAtkinson2008(): [1]
  0,ChiouYoungs2008(): [0]>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== ============ ============
source_model     grp_id trt                  eff_ruptures tot_ruptures
================ ====== ==================== ============ ============
source_model.xml 0      Active Shallow Crust 744          828         
================ ====== ==================== ============ ============

Exposure model
--------------
=============== ========
#assets         11      
#taxonomies     4       
deductibile     absolute
insurance_limit absolute
=============== ========

========================== ======= ====== === === ========= ==========
taxonomy                   mean    stddev min max num_sites num_assets
Adobe                      1.00000 0.0    1   1   2         2         
Stone-Masonry              1.00000 0.0    1   1   6         6         
Unreinforced-Brick-Masonry 1.00000 NaN    1   1   1         1         
Wood                       1.00000 0.0    1   1   2         2         
*ALL*                      1.00000 0.0    1   1   11        11        
========================== ======= ====== === === ========= ==========

Slowest sources
---------------
====== ========= ==== ===== ===== ============ ========= ========== ========= ========= ======
grp_id source_id code gidx1 gidx2 num_ruptures calc_time split_time num_sites num_split weight
====== ========= ==== ===== ===== ============ ========= ========== ========= ========= ======
0      229       A    0     4     264          0.32794   0.77234    203       38        50    
0      231       A    4     8     414          0.63440   1.19095    697       69        131   
0      232       A    8     12    150          0.22954   0.28549    270       30        44    
====== ========= ==== ===== ===== ============ ========= ========== ========= ========= ======

Computation times by source typology
------------------------------------
==== ========= ======
code calc_time counts
==== ========= ======
A    1.19187   3     
==== ========= ======

Duplicated sources
------------------
There are no duplicated sources

Information about the tasks
---------------------------
================== ======= ======= ======= ======= =======
operation-duration mean    stddev  min     max     outputs
read_source_models 0.04925 NaN     0.04925 0.04925 1      
split_filter       0.05996 NaN     0.05996 0.05996 1      
classical          1.20013 NaN     1.20013 1.20013 1      
build_hazard_stats 0.00670 0.00304 0.00414 0.01342 11     
================== ======= ======= ======= ======= =======

Fastest task
------------
taskno=1, weight=227, duration=1 s, sources="229 231 232"

======== ======= ======= ======= ======= ===
variable mean    stddev  min     max     n  
======== ======= ======= ======= ======= ===
nsites   8.54015 2.58393 1       11      137
weight   1.65823 0.32976 0.60000 1.98997 137
======== ======= ======= ======= ======= ===

Slowest task
------------
taskno=1, weight=227, duration=1 s, sources="229 231 232"

======== ======= ======= ======= ======= ===
variable mean    stddev  min     max     n  
======== ======= ======= ======= ======= ===
nsites   8.54015 2.58393 1       11      137
weight   1.65823 0.32976 0.60000 1.98997 137
======== ======= ======= ======= ======= ===

Data transfer
-------------
================== ======================================================================= ========
task               sent                                                                    received
read_source_models monitor=0 B fnames=0 B converter=0 B                                    3.85 KB 
split_filter       srcs=3.48 KB monitor=439 B srcfilter=253 B sample_factor=21 B seed=14 B 36.64 KB
classical          group=36.69 KB param=546 B monitor=345 B gsims=308 B src_filter=220 B   3.29 KB 
build_hazard_stats pgetter=34.64 KB monitor=3.8 KB hstats=737 B                            4.59 KB 
================== ======================================================================= ========

Slowest operations
------------------
======================== ========= ========= ======
operation                time_sec  memory_mb counts
======================== ========= ========= ======
total classical          1.20013   0.84766   1     
make_contexts            0.46622   0.0       792   
get_poes                 0.40171   0.0       744   
iter_ruptures            0.29973   0.0       137   
updating source_info     0.07393   0.0       1     
total build_hazard_stats 0.07365   0.65625   11    
combine pmaps            0.06469   0.65625   11    
total split_filter       0.05996   0.14844   1     
total read_source_models 0.04925   0.0       1     
building riskinputs      0.02455   0.0       1     
saving statistics        0.00641   0.0       11    
compute mean             0.00558   0.0       11    
managing sources         0.00541   0.0       1     
store source_info        0.00361   0.0       1     
saving probability maps  0.00134   0.0       1     
reading exposure         5.181E-04 0.0       1     
aggregate curves         3.390E-04 0.0       1     
======================== ========= ========= ======