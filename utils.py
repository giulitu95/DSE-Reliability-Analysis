'''
This file include utility functions
'''


'''
Find majority element in a list.
Note: The majority element is the element that appears more than n/2 times where n is the number of elements in the list.
'''

def majority_element(elem_list):
        index, counter = 0, 1
        
        for i in range(1, len(elem_list)):
            if elem_list[index] == elem_list[i]:
                counter += 1
            else:
                counter -= 1
                if counter == 0:
                    index = i
                    counter = 1
        
        return index
        #return [index], index

#print(majority_element([2, 1, 1, 2, 3, 1, 3, 1]))