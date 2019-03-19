==========
Queries
==========

With SharePlum you can retrieve list items by providing a View Name or by providing a list of Column Names (fields) and a query.  You don't have to provide a query.  Given a list of Column Names, SharePlum will return all of the data for those columns.  When you need to filter down this information, you can provide a query.  A query has three major elements: Where, OrderBy, and GroupBy.


Where
=====

The Where Element is probably the most commonly used. ::

    fields = ['Title', 'My Other Column']
    query = {'Where': [('Eq', 'My Other Column', 'Nice Value')]}
    sp_data = sp_list.GetListItems(fields=fields, query=query)

You don't pass a value if you are using IsNull. ::

    query = {'Where': [('IsNull', 'My Other Column')]}
    sp_data = sp_list.GetListItems(fields=fields, query=query)
    
You can use AND or OR for multiple conditions ::

    query = {'Where': ['And', ('Eq', 'Title', 'Good Title'),
                              ('Eq', 'My Other Column', 'Nice Value')]}

    query = {'Where': ['Or', ('Eq', 'Title', 'Good Title'),
                             ('Eq', 'My Other Column', 'Nice Value')]}
or use them both ::

    query = {'Where': ['Or',  ('Eq', 'My Other Column', 'Great Title'),
                       'And', ('Eq', 'My Other Column', 'Good Title'),
                              ('Eq', 'My Other Column', 'Nice Value')]}

Where Options:
--------------

* Eq: Equals
* Neq: Not Equal To
* Geq: Greater Than or Equal To
* Gt: Greater Than
* Leq: Less Than or Equal To
* Lt: Less Than
* IsNull: Value Is Null
* IsNotNull: Value is not Null
* BeginsWith: Begins With Text
* Contains: Contains Text


OrderBy
=======
With OrderBy you can provide a list of Columns that will be used to sort your data.  Ascending order is the default.  If that's all you need, you can just provide the Column Names::

    query = {'OrderBy': ['Title']}

If you want Descending order, you'll have to specify it. ::

    query = {'OrderBy': [('Title', 'DESCENDING')]}

GroupBy
=======
GroupBy can be used to group your data by Columns::

    query = {'GroupBy': ['Title']}
