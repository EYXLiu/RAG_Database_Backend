class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []
        
class BTree:
    def __init__(self, t=2):
        self.root = BTreeNode(leaf=True)
        self.t = t
        self.size = 0
        
    def search(self, key, node=None):
        if node is None:
            node = self.root
        
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and node.keys[i] == key:
            return True
        
        if node.leaf:
            return False
        
        return self.search(key, node.children[i])
    
    def insert(self, key: int):
        root = self.root
        self.size += 1
        if len(root.keys) == (2 * self.t) - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root
            
        self.insert_non_full(self.root, key)
        
    def insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self.insert_non_full(node.children[i], key)
        
    def split_child(self, parent, i):
        t = self.t
        child = parent.children[i]
        new_child = BTreeNode(leaf=child.leaf)
        
        parent.keys.insert(i, child.keys[t - 1])
        parent.children.insert(i + 1, new_child)
        
        new_child.keys = child.keys[t: (2 * t) - 1]
        child.keys= child.keys[:t - 1]
        
        if not child.leaf:
            new_child.children = child.children[t: 2 * t]
            child.children = child.children[:t]
            
    def delete(self, key, node=None):
        if node is None:
            node = self.root
            
        self.size -= 1
        t = self.t
        idx = self.find_key(node, key)
        
        if idx < len(node.keys) and node.keys[idx] == key:
            if node.leaf:
                node.keys.pop(idx)
            else: 
                self.delete_internal_node(node, idx)
        else: 
            if node.leaf:
                return
            
            child = node.children[idx]
            if len(child.keys) < t:
                self.fill(node, idx)
            if idx < len(node.keys) and node.keys[idx] == key:
                self.delete(key, node.children[idx + 1]) 
            else:
                self.delete(key, node.children[idx])
               
    def delete_internal_node(self, node, idx):
        t = self.t
        key = node.keys[idx]
        
        if len(node.children[idx].keys) >= t:
            pred_key = self.get_predecessor(node, idx)
            node.keys[idx] = pred_key
            self.delete(pred_key, node.children[idx])
        elif len(node.children[idx + 1].keys) >= t:
            succ_key = self.get_successor(node, idx)
            node.keys[idx] = succ_key
            self.delete(succ_key, node.children[idx + 1])
        else:
            self.merge(node, idx)
            self.delete(key, node.children[idx])
            
    def fill(self, node, idx):
        t = self.t
        
        if idx > 0 and len(node.children[idx - 1].keys) >= t:
            self.borrow_from_prev(node, idx)
        elif idx < len(node.children) - 1 and len(node.children[idx + 1].keys) >= t:
            self.borrow_from_next(node, idx)
        else:
            if idx < len(node.children) - 1:
                self.merge(node, idx)
            else:
                self.merge(node, idx - 1)
                
    def borrow_from_prev(self, node, idx):
        t = self.t
        child = node.children[idx]
        sibling = node.children[idx - 1]
        
        node.keys[idx - 1] = sibling.keys.pop()
        child.keys.insert(0, node.keys[idx - 1])
        
        if not sibling.leaf:
            child.children.insert(0, sibling.children.pop())
            
    def borrow_from_next(self, node, idx):
        t = self.t
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        node.keys[idx] = sibling.keys.pop(0)
        child.keys.append(node.keys[idx])
        
        if not sibling.leaf:
            child.children.append(sibling.children.pop(0))
            
    def merge(self, node, idx):
        t = self.t
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        child.keys.append(node.keys.pop(idx))
        
        child.keys.extend(sibling.keys)
        child.children.extend(sibling.children)
        
        node.children.pop(idx + 1)
    
    def get_predecessor(self, node, idx):
        current = node.children[idx]
        while not current.leaf:
            current = current.children[-1]
        return current.keys[-1]
    
    def get_successor(self, node, idx):
        current = node.children[idx + 1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]
    
    def find_key(self, node, key):
        idx = 0
        while idx < len(node.keys) and node.keys[idx] < key:
            idx += 1
        return idx
    
    def traverse(self, node=None):
        if node is None:
            node = self.root
        
        l = []
            
        for i in range(len(node.keys)):
            if not node.leaf:
                l += self.traverse(node.children[i])
            l.append(node.keys[i])
            
        if not node.leaf:
            l += self.traverse(node.children[len(node.keys)])
            
        return l
    
    def visualize(self, node=None):
        if node is None:
            node = self.root
        
        l = []
            
        for i in range(len(node.keys)):
            if not node.leaf:
                l.append(self.visualize(node.children[i]))
            l.append(node.keys[i])
            
        if not node.leaf:
            l.append(self.visuzalize(node.children[len(node.keys)]))
            
        return l
            
    def __len__(self):
        return self.size
    
    def max(self, node=None):
        if node is None:
            node = self.root
        
        if node.leaf:
            return int(node.keys[-1]) if node.keys else 0
        
        return self.max(node.children[-1])