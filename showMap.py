import matplotlib.pyplot as plt
import numpy as np

import csv

def showMap(isv, gm):
	################################################################
	## SHOW STATE (instantStateVector)
	################################################################
	# Show map
	plt.close("all")
	fig = plt.figure()
	fig.set_size_inches(26.4, 19.0)
	ax = plt.Axes(fig, [0., 0., 1., 1.])
	ax.set_axis_off()
	fig.add_axes(ax)

	im = plt.imread("pandemicMap.jpg")
	implot = plt.imshow(im)
	for k in gm['indexedCities'].keys():
		# Plot all cities with circles
		plt.scatter(x=[gm['mapXYs'][k-1][1]], y=[gm['mapXYs'][k-1][2]], c=gm['mapHexColors'][k], s=300, alpha=0.5)
		# Name all cities
		t=plt.text(gm['mapXYs'][k-1][1]-15, gm['mapXYs'][k-1][2]-25, gm['mapCityNames'][k], color=gm['mapHexColors'][k])
		t.set_bbox(dict(facecolor='#bbbbbb', alpha=0.9, edgecolor='white'))

	# Plot all city connections
	cityConns = np.transpose(np.where(gm['mapAdj'])) + 1
	for cci in np.arange(0,len(cityConns)):
		connXY = gm['mapXYs'][cityConns[cci]-1]
		plt.plot(connXY[:,1],connXY[:,2],'k',linewidth=5)

	# Plot all cubes (from instant state vector)
	isvblue = isv['blueCubesByCity']
	for ic in range(len(isvblue)):
		if isvblue[ic] > 0:
			nC = int(isvblue[ic])
			xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
		if isvblue[ic] > 1:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
		if isvblue[ic] > 2:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='^', c='blue', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
	isvyellow = isv['yellowCubesByCity']
	for ic in range(len(isvyellow)):
		if isvyellow[ic] > 0:
			nC = int(isvyellow[ic])
			xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
		if isvyellow[ic] > 1:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
		if isvyellow[ic] > 2:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='>', c='yellow', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
	isvblack = isv['blackCubesByCity']
	for ic in range(len(isvblack)):
		if isvblack[ic] > 0:
			nC = int(isvblack[ic])
			xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
		if isvblack[ic] > 1:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
		if isvblack[ic] > 2:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='v', c='black', s=4500, alpha=0.9, edgecolor='white', linewidth='7')
	isvred = isv['redCubesByCity']
	for ic in range(len(isvred)):
		if isvred[ic] > 0:
			nC = int(isvred[ic])
			xyC = gm['mapXYs'][gm['mapXYs'][:,0]==ic,1:3][0]
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=1500, alpha=0.5, edgecolor='white', linewidth='2')
		if isvred[ic] > 1:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=3000, alpha=0.7, edgecolor='white', linewidth='4')
		if isvred[ic] > 2:
			plt.scatter(x=[xyC[0]], y=[xyC[1]], marker='<', c='red', s=4500, alpha=0.9, edgecolor='white', linewidth='7')

	# Plot all player locations (from instant state vector)
	teamLocs = np.fliplr(np.transpose(np.where(np.transpose(isv['teamMemberCities']))))
	playerThetaOffs = 3.0*np.pi/4.0
	dTheta = 2*np.pi / gm['numTeamMembers']
	rPlayer = 12 # radius offset of player token from center of city
	for teami in range(gm['numTeamMembers']):
		thetaOffs = playerThetaOffs + teami*dTheta
		xyOffs = np.array([rPlayer*np.cos(thetaOffs),rPlayer*np.sin(thetaOffs)])
		xyTm = gm['mapXYs'][gm['mapXYs'][:,0]==teamLocs[teami][0],1:3][0]
		# Plot all team members with colored circles
		plt.scatter(x=[xyTm[0]+xyOffs[0]], y=[xyTm[1]+xyOffs[1]], c=gm['teamColors'][isv['teamSequence'][teami]], s=500, alpha=0.9, edgecolor='white')

	# SHOW RESEARCH FACILITIES
	researchFacilityCities = np.where(isv['researchFacilitiesByCity'])[0]
	for iRF in researchFacilityCities:
		plt.scatter(x=[gm['mapXYs'][iRF-1][1]], y=[gm['mapXYs'][iRF-1][2]], marker='s', facecolors='none', s=6000, alpha=0.9, edgecolors='white', linewidth='4')

	plt.show()
	fig.savefig('pandemicInit.png', dpi=100)
