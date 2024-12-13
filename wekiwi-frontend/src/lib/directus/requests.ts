import { PAGE_SIZE } from '$lib/config/constants';


// INFO: in the future the response will come from the ai server
export const requestContents = (
  type: string,
  circles: number[] | null,
  search: string | null,
  company_id: string,
  sort1: string,
  sort2: string,
  usercreated: string | null,
  userupdated: string | null,
  datecreated1: string | null,
  datelogic1: string | null,
  datecreated2: string | null,
  dateupdated1: string | null,
  datelogic2: string | null,
  dateupdated2: string | null,
  offset: number = 0,
) => {

  // Sort
  const sort: Array<string> = [...new Set([sort1, sort2].filter(Boolean))];

  const dateFilters = [];

  // Created Date Filter
  if (datecreated1 && datelogic1) {
    if (datelogic1 === '_between' && datecreated2) {
      dateFilters.push({
        date_created: {
          _between: [datecreated1, datecreated2],
        },
      });
    } else {
      dateFilters.push({
        date_created: {
          [datelogic1]: datecreated1,
        },
      });
    }
  }

  // Updated Date Filter
  if (dateupdated1 && datelogic2) {
    if (datelogic2 === '_between' && dateupdated2) {
      dateFilters.push({
        date_updated: {
          _between: [dateupdated1, dateupdated2],
        },
      });
    } else {
      dateFilters.push({
        date_updated: {
          [datelogic2]: dateupdated1,
        },
      });
    }
  }

  let userFilter = [];

  // User Filter
  // !!!This only filters the FIRST level!!!
  if (usercreated) {
    userFilter.push({ user_created: { username: { '_eq': usercreated } } });
  }
  if (userupdated) {
    userFilter.push({ user_updated: { username: { '_eq': userupdated } } });
  }

  return {
    filter: {
      "_and": [
        // Filter by company_id
        { company_id: { '_eq': +company_id } },
        // Conditionally add filter for circles if defined and has values
        ...((circles && circles.length > 0) ? [{
          circle_contents: {
            circle_id: {
              circle_id: { '_in': circles }
            }
          }
        },
        ] : []),
        // Conditionally filter text or title of content and subContent
        ...(search ? [{
          "_or": [
            { text: { '_icontains': search } },
            { title: { '_icontains': search } },
            { child_id: { text: { '_icontains': search } } },
            { child_id: { title: { '_icontains': search } } }
          ]
        }] : []),
        // Conditionally add filter for dates and datelogics
        ...dateFilters,
        // Conditionally add filter for user
        ...userFilter,
        { content_type: { '_eq': type } },
        { parent_id: { '_null': true } },
      ]
    },
    offset: offset,
    limit: PAGE_SIZE,
    sort: sort,
    deep: {
      interaction_id: {
        _filter: {
          interaction_type: {
            _eq: 'like'
          },
        },
      },
      child_id: {
        interaction_id: {
          _filter: {
            interaction_type: {
              _eq: 'like',
            },
          },
        },
      }
    },
    fields: [
      "content_id",
      'content_type',
      "title",
      "text",
      'date_created',
      'date_updated',
      'parent_id',
      {
        interaction_id: ['interaction_id']
      },
      {
        user_created: ['avatar', 'username'],
        user_updated: ['avatar', 'username'],
      },
      {
        child_id: [
          'content_id',
          'content_type',
          'title',
          'text',
          'date_created',
          'date_updated',
          'child_id',
          'parent_id',
          {
            interaction_id: ['interaction_id']
          },
          {
            user_created: ['avatar', 'username'],
            user_updated: ['avatar', 'username']
          },
        ]
      }
    ],
  }
}

export const requestVectorContents = (
  type: string,
  circles: number[] | null,
  search: string | null,
  company_id: string,
  usercreated: string | null,
  userupdated: string | null,
  datecreated1: string | null,
  datelogic1: string | null,
  datecreated2: string | null,
  dateupdated1: string | null,
  datelogic2: string | null,
  dateupdated2: string | null,
  offset: number | null = null
) => {
  let filter = '';

  // Add type filter
  if (type) {
    filter += `content_type == '${type}'`;
  }

  // Date Logic Mapping
  const dateLogicMapping: { [key: string]: string } = {
    '_between': 'BETWEEN',
    '_lt': '<',
    '_gt': '>',
    '_eq': '=',
    '_neq': '!=',
    '_lte': '<=',
    '_gte': '>='
  };

  // Add date created filter
  if (datecreated1 && datelogic1) {
    const convertedDatecreated1 = dateToUnixTimestamp(datecreated1);
    if (datelogic1 === '_between' && datecreated2) {
      const convertedDatecreated2 = dateToUnixTimestamp(datecreated2);
      filter += ` and date_created ${dateLogicMapping[datelogic1]} ${convertedDatecreated1} AND ${convertedDatecreated2}`; 
    } else {
      filter && (filter += ' and ');
      filter += `date_created ${dateLogicMapping[datelogic1] || '>='} ${convertedDatecreated1}`;
    }
  }

  // Add date updated filter
  if (dateupdated1 && datelogic2) {
    const convertedDateupdated1 = dateToUnixTimestamp(dateupdated1);
    if (datelogic2 === '_between' && dateupdated2) {
      const convertedDateupdated2 = dateToUnixTimestamp(dateupdated2);
      filter += ` and date_updated ${dateLogicMapping[datelogic2]} ${convertedDateupdated1} AND ${convertedDateupdated2}`;
    } else {
      filter && (filter += ' and ');
      filter += `date_updated ${dateLogicMapping[datelogic2] || '>='} ${convertedDateupdated1}`;
    }
  }

  // Add user created filter
  if (usercreated) {
    filter && (filter += ' and ');
    filter += `user_created == '${usercreated}'`;
  }

  // Add user updated filter
  if (userupdated) {
    filter && (filter += ' and ');
    filter += `user_updated == '${userupdated}'`;
  }

  return {
    query: search,
    company_id: +company_id,
    circle_ids: circles,
    rerank: true,
    offset: offset || null,
    //page_size: PAGE_SIZE, //default used in backend
    filter: filter,
  };
};

// Helper function to convert date string to Unix timestamp (seconds)
function dateToUnixTimestamp(dateString: string): number {
  const date = new Date(dateString);
  return Math.floor(date.getTime() / 1000); 
}