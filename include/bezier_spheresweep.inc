/* bezier_spheresweep.inc
 * created by Cheng-Han Tsai
 * This file is licensed under the terms of the CC-LGPL.
*/


/****************************

each bezier curve segment includes 'resolution+1' amout of spheres and cones.
each sphere and cones are union/merge.
the size of '_points_array' must be the same as '_radius_array'
****************************/
#include "shapes.inc"

#macro Shape_Bezierpoints_Sphere_Sweep(_merge_shape, _resolution, _points_array, _radius_array)
//input adjusting and inspection
#if(_resolution <= 1)
    #local res = 1;
#else
    #local res = int(_resolution);
#end
#if(dimensions(_points_array) != 1 | dimensions(_radius_array) != 1)
    #error ""
#elseif(div(dimension_size(_points_array,1),4) - dimension_size(_points_array,1)/4 != 0)
    #error ""
#elseif(dimension_size(_points_array,1) != dimension_size(_radius_array,1))
    #error ""
#else
    #local n_of_seg = div(dimension_size(_points_array,1), 4);
    #local ctrl_pts_array = array[n_of_seg]
    #local ctrl_rs_array = array[n_of_seg]
    #for(i, 0, n_of_seg-1)
        #local ctrl_pts_array[i] = array[4] {_points_array[4*i], _points_array[4*i+1], _points_array[4*i+2], _points_array[4*i+3]}
        #local ctrl_rs_array[i] = array[4] {abs(_radius_array[4*i]), abs(_radius_array[4*i+1]), abs(_radius_array[4*i+2]), abs(_radius_array[4*i+3])}
    #end
#end

//drawing
#local mockup1 =
#if(_merge_shape) merge{ #else union{ #end
    #for(i, 0, n_of_seg-1)
        #local has_head = true;
        #if(i = 0)
            #if(vlength(ctrl_pts_array[i][0]-ctrl_pts_array[n_of_seg-1][3]) = 0 & ctrl_rs_array[i][0]-ctrl_rs_array[n_of_seg-1][3] <= 0)
                #local has_head = false;
            #end
        #else
            #if(vlength(ctrl_pts_array[i][0]-ctrl_pts_array[i-1][3]) = 0 & ctrl_rs_array[i][0]-ctrl_rs_array[i-1][3] <= 0)
                #local has_head = false;
            #end
        #end
        #if(has_head = true)
            sphere{
            ctrl_pts_array[i][0], ctrl_rs_array[i][0]
            }
        #end
        #local para_t = (1/2)/res;
        #local this_point = ctrl_pts_array[i][0]*pow(1-para_t,3) + ctrl_pts_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_pts_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_pts_array[i][3]*pow(para_t,3);
        #local this_radius = ctrl_rs_array[i][0]*pow(1-para_t,3) + ctrl_rs_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_rs_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_rs_array[i][3]*pow(para_t,3);
        #if(vlength(this_point-ctrl_pts_array[i][0]) > abs(this_radius-ctrl_rs_array[i][0]))
            object{
            Connect_Spheres(ctrl_pts_array[i][0], ctrl_rs_array[i][0], this_point, this_radius)
            }
        #end
        sphere{
        this_point, this_radius
        }
        #for(j, 1, res-1)
            #local last_point = this_point;
            #local last_radius = this_radius;
            #local para_t = (1/2+j)/res;
            #local this_point = ctrl_pts_array[i][0]*pow(1-para_t,3) + ctrl_pts_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_pts_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_pts_array[i][3]*pow(para_t,3);
            #local this_radius = ctrl_rs_array[i][0]*pow(1-para_t,3) + ctrl_rs_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_rs_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_rs_array[i][3]*pow(para_t,3);
            #if(vlength(this_point-last_point) > abs(this_radius-last_radius))
                object{
                Connect_Spheres(last_point, last_radius, this_point, this_radius)
                }
            #end
            sphere{
            this_point, this_radius
            }
        #end
        #local last_point = this_point;
        #local last_radius = this_radius;
        #local this_point = ctrl_pts_array[i][3];
        #local this_radius = ctrl_rs_array[i][3];
        #if(vlength(this_point-last_point) > abs(this_radius-last_radius))
            object{
            Connect_Spheres(last_point, last_radius, this_point, this_radius)
            }
        #end
        sphere{
        this_point, this_radius
        }
    #end
}
mockup1
#end
