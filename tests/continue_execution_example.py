import requests
import json
import uuid
from config import shared_dict

if __name__ == '__main__':

    base_url = 'http://localhost:9999/api/v1'
    
    res_dict = create_kernel(base_url)
    execution_id_1 = res_dict.get('execution_id')
    kernel_dict = get_kernel(base_url, execution_id_1)
    
    res_dict =  create_kernel(base_url)
    execution_id_2 = res_dict.get('execution_id')
    kernel_dict = get_kernel(base_url, execution_id_2)
    
    res_dict =  create_kernel(base_url)
    execution_id_3 = res_dict.get('execution_id')
    kernel_dict = get_kernel(base_url, execution_id_3)    
    
    kernels_dict = get_kernels(base_url)
    
    print('Prepare an existing kernel. Execution server should not create a new kernel and return 204 response.')
    kernel_dict_1 = get_kernel(base_url, execution_id_1)            
    prepare_kernel(base_url, execution_id_1)
    get_kernels(base_url)         
    
    check_again = input('Restart JKG and check kernel again? (y/n)')
    if check_again == "y":
        kernel_dict_2 = get_kernel(base_url, execution_id_2)        
        
        prepare_kernel(base_url, execution_id_2)
        get_kernels(base_url)        
        
    check_again = input('Restart execution service and check kernel again? (y/n)')

    if check_again == "y":
        kernel_dict_3 = get_kernel(base_url, execution_id_3) 
                
        prepare_kernel(base_url, execution_id_3)
        get_kernels(base_url)        
