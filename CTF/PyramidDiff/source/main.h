#define CT_INVALID_SCORE        9999

typedef struct _CT_ChannelRec {
//	int id;
//	int conformant;
	int rDepth;
	int gDepth;
	int bDepth;
	int aDepth;
	int lDepth;
//	int maskSize;
//	int cSpace;
} CT_ChannelRec;

CT_ChannelRec channelInfo;
